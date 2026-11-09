"""Stage 3b: build one row of model features per game.

The golden rule: a feature for a game may only use information that was
known BEFORE kickoff. Using anything from the game itself (or later games)
is "data leakage" and makes a model look far better than it really is.
tests/test_features.py checks this rule automatically.

Run from the repo root (inside the virtual environment):
    python src/features.py
"""

import pandas as pd

from analysis import DATA_PATH, load_games_df

# Relocated franchises get one code, so the Rams' history doesn't restart
# when they moved from St. Louis to Los Angeles.
FRANCHISE = {"STL": "LA", "SD": "LAC", "OAK": "LV"}

# The columns a model is allowed to use. Every one is known before kickoff.
FEATURE_COLUMNS = [
    "home_pf_last3", "home_pa_last3", "home_win_pct",
    "away_pf_last3", "away_pa_last3", "away_win_pct",
    "home_rest", "away_rest", "rest_diff", "div_game",
    "pf_last3_diff", "pa_last3_diff", "win_pct_diff",
]


def team_game_rows(df):
    """Turn each game into two rows, one from each team's point of view.

    Rolling stats are per team, and a team appears as home in some games
    and away in others. One row per (team, game) puts all of a team's
    games in a single column, so we can sort them by date.
    """
    home = pd.DataFrame({
        "game_id": df["game_id"], "season": df["season"], "gameday": df["gameday"],
        "team": df["home_team"],
        "points_for": df["home_score"], "points_against": df["away_score"],
    })
    away = pd.DataFrame({
        "game_id": df["game_id"], "season": df["season"], "gameday": df["gameday"],
        "team": df["away_team"],
        "points_for": df["away_score"], "points_against": df["home_score"],
    })
    rows = pd.concat([home, away], ignore_index=True)
    rows["team"] = rows["team"].replace(FRANCHISE)
    return rows


def win_credit(points_for, points_against):
    """1 for a win, 0.5 for a tie, 0 for a loss (the NFL's standings rule)."""
    credit = (points_for > points_against).astype(float)
    credit[points_for == points_against] = 0.5
    return credit


def add_team_history(rows):
    """Add pre-game rolling stats to each (team, game) row.

    The key trick is shift(1): it moves every value down one row within a
    team, so a game only ever sees the games BEFORE it, never itself.
    """
    rows = rows.sort_values(["team", "gameday", "game_id"]).copy()
    by_team = rows.groupby("team")

    # Average of the previous 3 games (fewer if the team has fewer so far).
    # Rolls across seasons, so week 1 uses the end of last season.
    for col, new in [("points_for", "pf_last3"), ("points_against", "pa_last3")]:
        rows[new] = by_team[col].transform(
            lambda s: s.shift(1).rolling(3, min_periods=1).mean())

    # Season win % so far: wins and games BEFORE this one, this season only
    rows["credit"] = win_credit(rows["points_for"], rows["points_against"])
    by_team_season = rows.groupby(["team", "season"])
    prior_wins = by_team_season["credit"].cumsum() - rows["credit"]
    prior_games = by_team_season.cumcount()  # 0 for the first game, 1 next...
    # Before a team's first game there is no record; 0.5 = "average team"
    rows["win_pct"] = (prior_wins / prior_games).where(prior_games > 0, 0.5)
    return rows.drop(columns="credit")


def build_features(df):
    """Return one row per game: identifiers, target info, and FEATURE_COLUMNS."""
    df = df.copy()
    df["gameday"] = pd.to_datetime(df["gameday"])
    history = add_team_history(team_game_rows(df))
    stats = history[["game_id", "team", "pf_last3", "pa_last3", "win_pct"]]

    out = df[["game_id", "season", "week", "game_type", "gameday",
              "home_team", "away_team", "home_score", "away_score",
              "spread_line", "home_rest", "away_rest", "div_game"]].copy()
    for side in ("home", "away"):
        side_stats = stats.rename(columns={
            "team": f"{side}_franchise",
            "pf_last3": f"{side}_pf_last3",
            "pa_last3": f"{side}_pa_last3",
            "win_pct": f"{side}_win_pct",
        })
        out[f"{side}_franchise"] = out[f"{side}_team"].replace(FRANCHISE)
        out = out.merge(side_stats, on=["game_id", f"{side}_franchise"], how="left")

    # Differences give the model one number per matchup: "how much better is
    # the home team on this stat?"
    out["rest_diff"] = out["home_rest"] - out["away_rest"]
    out["pf_last3_diff"] = out["home_pf_last3"] - out["away_pf_last3"]
    out["pa_last3_diff"] = out["home_pa_last3"] - out["away_pa_last3"]
    out["win_pct_diff"] = out["home_win_pct"] - out["away_win_pct"]
    return out.drop(columns=["home_franchise", "away_franchise"])


def main():
    features = build_features(load_games_df(DATA_PATH))
    print(f"{len(features)} games, {len(FEATURE_COLUMNS)} features\n")
    print("Features for the most recent game:")
    print(features[["game_id"] + FEATURE_COLUMNS].tail(1).T.to_string())


if __name__ == "__main__":
    main()
