"""Every SQL query the API runs, written by hand (no ORM).

Each function takes an open connection and returns plain Python values.
Values always go in through ? placeholders, never through string
formatting, so a request like /teams/KC';DROP TABLE games;-- is just a
team name that doesn't exist, not SQL that runs.

SQLite tricks used below:
  * (a > b) evaluates to 1 or 0, so SUM(a > b) counts rows where a > b.
  * Any comparison with NULL gives NULL, and SUM() skips NULLs.
  * CASE WHEN ... THEN ... ELSE ... END is SQL's if/else.
"""

# ---------- predictions ----------

LATEST_PREDICTED_SEASON = "SELECT MAX(test_season) FROM model_runs"

PREDICTIONS_FOR_WEEK = """
SELECT g.game_id, g.season, g.week, g.gameday, g.home_team, g.away_team,
       p.home_win_prob,
       -- The model picks the home team when P(home win) > 0.5,
       -- the same rule scikit-learn's predict() uses.
       CASE WHEN p.home_win_prob > 0.5 THEN g.home_team ELSE g.away_team END
           AS predicted_winner,
       g.spread_line,
       CASE WHEN g.spread_line > 0 THEN g.home_team
            WHEN g.spread_line < 0 THEN g.away_team
            ELSE NULL                    -- no line yet, or a pick'em
       END AS vegas_favorite,
       CASE WHEN g.home_score IS NULL THEN 'scheduled' ELSE 'final' END AS status,
       g.home_score, g.away_score,
       CASE WHEN g.home_score IS NULL OR g.home_score = g.away_score THEN NULL
            WHEN (p.home_win_prob > 0.5) = (g.home_score > g.away_score) THEN 1
            ELSE 0
       END AS correct
FROM games AS g
JOIN predictions AS p ON p.game_id = g.game_id   -- keep only predicted games
WHERE g.season = ? AND g.week = ?
ORDER BY g.gameday, g.game_id
"""


def latest_predicted_season(conn):
    return conn.execute(LATEST_PREDICTED_SEASON).fetchone()[0]


def predictions_for_week(conn, season, week):
    rows = conn.execute(PREDICTIONS_FOR_WEEK, (season, week)).fetchall()
    return [dict(row) for row in rows]


# ---------- teams ----------

TEAM_BY_ABBR = "SELECT abbr, name, conference, division FROM teams WHERE abbr = ?"

LATEST_PLAYED_SEASON = """
SELECT MAX(season) FROM team_games
WHERE team = ? AND points_for IS NOT NULL
"""

# Aggregate functions (COUNT, SUM, AVG) collapse all matching rows into one.
SEASON_STATS = """
SELECT COUNT(*)                                   AS games,
       SUM(points_for > points_against)           AS wins,
       SUM(points_for < points_against)           AS losses,
       SUM(points_for = points_against)           AS ties,
       SUM(points_for)                            AS points_for,
       SUM(points_against)                        AS points_against,
       SUM(points_for - points_against)           AS point_diff,
       ROUND(AVG(points_for), 1)                  AS avg_points_for,
       ROUND(AVG(points_against), 1)              AS avg_points_against,
       SUM(is_home = 1 AND points_for > points_against) AS home_wins,
       SUM(is_home = 1 AND points_for < points_against) AS home_losses,
       SUM(is_home = 0 AND points_for > points_against) AS away_wins,
       SUM(is_home = 0 AND points_for < points_against) AS away_losses
FROM team_games
WHERE team = ? AND season = ?
  AND game_type = 'REG'              -- standings count the regular season only
  AND points_for IS NOT NULL         -- played games only
"""

# The last N played games up to the end of the chosen season, newest first.
# Like the model's last-3 feature, this can reach back into the previous
# season and includes playoff games.
RECENT_GAMES = """
SELECT game_id, season, week, gameday, opponent,
       CASE WHEN is_home = 1 THEN 'home' ELSE 'away' END AS home_away,
       points_for, points_against,
       CASE WHEN points_for > points_against THEN 'W'
            WHEN points_for < points_against THEN 'L'
            ELSE 'T'
       END AS result
FROM team_games
WHERE team = ? AND season <= ? AND points_for IS NOT NULL
ORDER BY gameday DESC
LIMIT ?
"""


def team_by_abbr(conn, abbr):
    row = conn.execute(TEAM_BY_ABBR, (abbr,)).fetchone()
    return dict(row) if row else None


def latest_played_season(conn, abbr):
    return conn.execute(LATEST_PLAYED_SEASON, (abbr,)).fetchone()[0]


def season_stats(conn, abbr, season):
    row = dict(conn.execute(SEASON_STATS, (abbr, season)).fetchone())
    # With zero matching rows, COUNT gives 0 but SUM/AVG give NULL.
    return {**row, "season": season} if row["games"] else None


def recent_games(conn, abbr, season, limit=5):
    rows = conn.execute(RECENT_GAMES, (abbr, season, limit)).fetchall()
    return [dict(row) for row in rows]


# ---------- model accuracy ----------

# One row per model run (= per test season). JOIN links each prediction to
# its game (for the result) and its run (for the training seasons). GROUP BY
# makes the SUMs count separately for each run.
ACCURACY_BY_SEASON = """
SELECT r.test_season                                         AS season,
       r.train_first, r.train_last,
       COUNT(*)                                              AS games,
       SUM((p.home_win_prob > 0.5) = (g.home_score > g.away_score)) AS model_correct,
       SUM(g.home_score > g.away_score)                      AS home_correct,
       -- Vegas favorite = home if spread_line >= 0 (pick'em goes to home),
       -- the same rule as vegas_favorite_baseline() in src/model.py.
       SUM((g.spread_line >= 0) = (g.home_score > g.away_score)) AS vegas_correct,
       -- A subquery: a SELECT inside a SELECT, run once per run_id.
       (SELECT COUNT(*) FROM predictions AS p2
        JOIN games AS g2 ON g2.game_id = p2.game_id
        WHERE p2.run_id = r.run_id AND g2.home_score IS NULL) AS games_remaining
FROM predictions AS p
JOIN games AS g      ON g.game_id = p.game_id
JOIN model_runs AS r ON r.run_id = p.run_id
WHERE g.home_score IS NOT NULL           -- played
  AND g.home_score != g.away_score       -- ties have no right answer
GROUP BY r.run_id
ORDER BY r.test_season
"""


def accuracy_by_season(conn):
    return [dict(row) for row in conn.execute(ACCURACY_BY_SEASON).fetchall()]
