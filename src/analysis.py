"""Stage 2: the same questions as Stage 1, plus new ones, using pandas.

Run from the repo root (inside the virtual environment):
    python src/analysis.py
"""

import pandas as pd

import explore  # Stage 1, used to cross-check that both versions agree

DATA_PATH = "data/games.csv"


def load_games_df(path):
    """Read the games CSV into a DataFrame with only played games.

    pandas reads blank scores as NaN ("not a number"), so dropping rows
    with NaN scores removes unplayed games.
    """
    df = pd.read_csv(path)
    df = df.dropna(subset=["home_score", "away_score"])
    # NaN forces score columns to float (17.0); back to int now they're gone
    df["home_score"] = df["home_score"].astype(int)
    df["away_score"] = df["away_score"].astype(int)
    return df


def load_schedule_df(path):
    """Read every game in the CSV, including ones not played yet.

    Unplayed games keep NaN scores (so score columns stay float). Use this
    when you need to predict upcoming games; use load_games_df for analysis.
    """
    return pd.read_csv(path)


def filter_season(df, season=None):
    """Return rows for one season, or the whole DataFrame if season is None."""
    if season is None:
        return df
    return df[df["season"] == season]


# ---------- Stage 1 questions, redone in pandas ----------

def count_home_wins(df, season=None):
    """Return {"home": n, "away": n, "tie": n}, same as the Stage 1 version."""
    df = filter_season(df, season)
    return {
        "home": int((df["home_score"] > df["away_score"]).sum()),
        "away": int((df["home_score"] < df["away_score"]).sum()),
        "tie": int((df["home_score"] == df["away_score"]).sum()),
    }


def home_win_pct(df, season=None):
    """Home wins / decided games (ties excluded), or None if none decided."""
    counts = count_home_wins(df, season)
    decided = counts["home"] + counts["away"]
    return counts["home"] / decided if decided else None


def points_by_team(df, season=None):
    """Total points per team (home + away) as a Series, highest first."""
    df = filter_season(df, season)
    home = df.groupby("home_team")["home_score"].sum()
    away = df.groupby("away_team")["away_score"].sum()
    # add(fill_value=0) keeps a team even if it only appears on one side
    return home.add(away, fill_value=0).astype(int).sort_values(ascending=False)


def top_scoring_team(df, season=None):
    """Return (team, points) for the highest-scoring team."""
    totals = points_by_team(df, season)
    return totals.index[0], int(totals.iloc[0])


def average_total_points(df, season=None):
    """Average combined score per game."""
    df = filter_season(df, season)
    return (df["home_score"] + df["away_score"]).mean()


# ---------- New questions ----------

def home_win_pct_by_season(df):
    """Home win % for each season, ignoring neutral-site games and ties.

    Neutral-site games (Super Bowls, some international games) have a
    "home" team on paper only, so they would blur a home-field question.
    """
    df = df[(df["location"] == "Home") & (df["home_score"] != df["away_score"])]
    home_won = df["home_score"] > df["away_score"]
    # mean of True/False values = fraction that are True
    return home_won.groupby(df["season"]).mean()


def compare_eras(by_season, split_year=2015):
    """Average home win % before vs from `split_year` (full seasons only)."""
    early = by_season[by_season.index < split_year].mean()
    late = by_season[by_season.index >= split_year].mean()
    return early, late


def add_underdog_columns(df):
    """Add `underdog` and `underdog_won` columns based on spread_line.

    In nflverse, spread_line is the home team's expected winning margin:
    positive = home favored, negative = away favored. Pick'em games
    (spread_line == 0) have no underdog and are dropped.
    """
    df = df[df["spread_line"] != 0].copy()
    home_favored = df["spread_line"] > 0
    # where(cond, other): keep the value where cond is True, else use other
    df["underdog"] = df["away_team"].where(home_favored, df["home_team"])
    # result = home - away. Away underdog wins if result < 0; home underdog
    # wins if result > 0. A tie (result == 0) is not an underdog win.
    away_dog_won = df["result"] < 0
    home_dog_won = df["result"] > 0
    df["underdog_won"] = away_dog_won.where(home_favored, home_dog_won)
    return df


def underdog_win_rates(df, min_games=20):
    """Per-team win rate when playing as the underdog.

    Teams with fewer than `min_games` underdog games are dropped, because a
    rate from a handful of games is mostly noise.
    """
    dogs = add_underdog_columns(df)
    table = dogs.groupby("underdog")["underdog_won"].agg(games="count", wins="sum")
    table["win_pct"] = table["wins"] / table["games"]
    table = table[table["games"] >= min_games]
    return table.sort_values("win_pct", ascending=False)


def overall_underdog_win_pct(df):
    """Fraction of all non-pick'em games won by the underdog."""
    return add_underdog_columns(df)["underdog_won"].mean()


# ---------- Running it ----------

def check_matches_stage1(df, games, season=None):
    """Assert the pandas answers equal the plain-Python answers."""
    assert count_home_wins(df, season) == explore.count_home_wins(games, season)
    assert top_scoring_team(df, season) == explore.top_scoring_team(games, season)
    assert abs(average_total_points(df, season)
               - explore.average_total_points(games, season)) < 1e-9


def main():
    df = load_games_df(DATA_PATH)
    games = explore.load_games(DATA_PATH)

    for season in (None, 2025):
        check_matches_stage1(df, games, season)
    print("pandas answers match Stage 1 (all seasons and 2025)\n")

    counts = count_home_wins(df)
    team, points = top_scoring_team(df)
    print(f"Home / away / ties: {counts['home']} / {counts['away']} / {counts['tie']}")
    print(f"Home win %:         {home_win_pct(df):.1%}")
    print(f"Top scoring team:   {team} ({points} points)")
    print(f"Avg total points:   {average_total_points(df):.2f}\n")

    # Only complete seasons, so a half-finished current season doesn't skew it
    last_full = df.loc[df["game_type"] == "SB", "season"].max()
    by_season = home_win_pct_by_season(df[df["season"] <= last_full])
    print("Home win % by season (non-neutral, no ties):")
    print(by_season.map("{:.1%}".format).to_string(), "\n")
    early, late = compare_eras(by_season)
    print(f"1999-2014 average: {early:.1%}   2015-{last_full} average: {late:.1%}\n")

    print(f"Underdogs win {overall_underdog_win_pct(df):.1%} of games\n")
    rates = underdog_win_rates(df)
    rates["win_pct"] = rates["win_pct"].map("{:.1%}".format)
    print("Underdog win rate by team (min 20 games as underdog):")
    print(rates.to_string())


if __name__ == "__main__":
    main()
