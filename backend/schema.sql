-- The database layout for the NFL predictor API.
-- pipeline/build_db.py runs this file on a fresh, empty database.
--
-- SQLite notes:
--   * INTEGER, REAL and TEXT are the main column types.
--   * NULL means "no value". An unplayed game has NULL scores.
--   * SQLite has no boolean type: comparisons like (a > b) give 1 or 0.

-- Turn on foreign key checks (SQLite leaves them off by default).
PRAGMA foreign_keys = ON;

-- One row per current franchise. Old codes (STL, SD, OAK) are mapped to the
-- current ones before games are inserted, so every game points at a row here.
CREATE TABLE teams (
    abbr        TEXT PRIMARY KEY,          -- e.g. 'KC'
    name        TEXT NOT NULL,             -- e.g. 'Kansas City Chiefs'
    conference  TEXT NOT NULL CHECK (conference IN ('AFC', 'NFC')),
    division    TEXT NOT NULL              -- e.g. 'AFC West'
);

-- One row per game, played or not.
CREATE TABLE games (
    game_id      TEXT PRIMARY KEY,         -- e.g. '2026_08_CAR_GB'
    season       INTEGER NOT NULL,
    week         INTEGER NOT NULL,
    game_type    TEXT NOT NULL,            -- 'REG', 'WC', 'DIV', 'CON', 'SB'
    gameday      TEXT NOT NULL,            -- ISO date 'YYYY-MM-DD' sorts correctly as text
    home_team    TEXT NOT NULL REFERENCES teams(abbr),
    away_team    TEXT NOT NULL REFERENCES teams(abbr),
    home_score   INTEGER,                  -- NULL until the game is played
    away_score   INTEGER,
    spread_line  REAL,                     -- home team's expected margin; NULL if no line yet
    home_rest    INTEGER,
    away_rest    INTEGER,
    div_game     INTEGER NOT NULL          -- 1 = divisional game, 0 = not
);

-- Indexes make lookups fast, like the index at the back of a book.
-- Without one, "WHERE season = 2026 AND week = 11" reads every row.
CREATE INDEX idx_games_season_week ON games (season, week);
CREATE INDEX idx_games_home ON games (home_team);
CREATE INDEX idx_games_away ON games (away_team);

-- One row per trained model. Each run predicts exactly one test season.
--   2025 run: trained on 2018-2024, so its 2025 predictions are a fair test.
--   2026 run: trained on 2018-2025, used for this season's predictions.
CREATE TABLE model_runs (
    run_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at    TEXT NOT NULL,           -- ISO timestamp
    train_first   INTEGER NOT NULL,        -- first training season
    train_last    INTEGER NOT NULL,        -- last training season
    test_season   INTEGER NOT NULL UNIQUE, -- the season this run predicts
    train_games   INTEGER NOT NULL,
    coefficients  TEXT NOT NULL            -- JSON: {"feature": coefficient, ...}
);

-- One row per predicted game. A game is predicted by exactly one run:
-- the run whose test_season is that game's season.
CREATE TABLE predictions (
    game_id        TEXT PRIMARY KEY REFERENCES games(game_id),
    run_id         INTEGER NOT NULL REFERENCES model_runs(run_id),
    home_win_prob  REAL NOT NULL CHECK (home_win_prob BETWEEN 0 AND 1)
);

-- A VIEW is a saved SELECT you can query like a table. It stores no data.
-- This one turns each game into two rows, one from each team's side, so
-- "all of KC's games" is a simple WHERE team = 'KC' instead of
-- WHERE home_team = 'KC' OR away_team = 'KC' plus flipping the scores.
-- (Same idea as team_game_rows() in src/features.py, written in SQL.)
CREATE VIEW team_games AS
    SELECT game_id, season, week, game_type, gameday,
           home_team AS team, away_team AS opponent, 1 AS is_home,
           home_score AS points_for, away_score AS points_against
    FROM games
    UNION ALL
    SELECT game_id, season, week, game_type, gameday,
           away_team AS team, home_team AS opponent, 0 AS is_home,
           away_score AS points_for, home_score AS points_against
    FROM games;
