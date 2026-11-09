"""Stage 1: answer basic questions about NFL games using only plain Python.

No pandas here on purpose: doing it by hand with lists and dicts shows
exactly what pandas will later do for us in one line.

Run from the repo root:
    python3 src/explore.py
"""

import csv

DATA_PATH = "data/games.csv"


def load_games(path):
    """Read the games CSV and return a list of dicts, one per *played* game.

    Scores, season and week are converted to int so callers can do math
    on them. Unplayed (future) games are skipped.
    """
    games = []
    with open(path) as f:
        for row in csv.DictReader(f):
            # Games that haven't been played yet have blank scores
            if row["home_score"] == "" or row["away_score"] == "":
                continue
            # csv gives us strings; "17" + "14" would be "1714", not 31
            row["home_score"] = int(row["home_score"])
            row["away_score"] = int(row["away_score"])
            row["season"] = int(row["season"])
            row["week"] = int(row["week"])
            games.append(row)
    return games


def filter_season(games, season=None):
    """Return only the games from `season`, or all games if season is None."""
    if season is None:
        return games
    return [g for g in games if g["season"] == season]


def count_home_wins(games, season=None):
    """Count home wins, away wins and ties.

    Returns a dict like {"home": 4100, "away": 3200, "tie": 16}.
    Ties get their own bucket so they are never silently counted as a
    home loss.
    """
    counts = {"home": 0, "away": 0, "tie": 0}
    for g in filter_season(games, season):
        if g["home_score"] > g["away_score"]:
            counts["home"] += 1
        elif g["home_score"] < g["away_score"]:
            counts["away"] += 1
        else:
            counts["tie"] += 1
    return counts


def home_win_pct(games, season=None):
    """Fraction of games *with a winner* that the home team won.

    Ties are left out of the denominator: a tie is neither a home win nor
    a home loss, so it shouldn't drag the percentage up or down.
    Returns None if there are no decided games (avoids dividing by zero).
    """
    counts = count_home_wins(games, season)
    decided = counts["home"] + counts["away"]
    if decided == 0:
        return None
    return counts["home"] / decided


def points_by_team(games, season=None):
    """Total points scored by each team, counting home AND away games.

    Returns a dict like {"KC": 9876, "BUF": 9500, ...}.
    """
    totals = {}
    for g in filter_season(games, season):
        # A team's points come from both sides of the schedule, so add both
        home, away = g["home_team"], g["away_team"]
        totals[home] = totals.get(home, 0) + g["home_score"]
        totals[away] = totals.get(away, 0) + g["away_score"]
    return totals


def top_scoring_team(games, season=None):
    """Return (team, points) for the team that scored the most points.

    Returns None if there are no games.
    """
    totals = points_by_team(games, season)
    if not totals:
        return None
    best_team = max(totals, key=totals.get)
    return best_team, totals[best_team]


def average_total_points(games, season=None):
    """Average combined score (home + away) per game, or None if no games."""
    selected = filter_season(games, season)
    if not selected:
        return None
    total = sum(g["home_score"] + g["away_score"] for g in selected)
    return total / len(selected)


def print_summary(games, season=None):
    """Print the answers to every Stage 1 question for one season (or all)."""
    label = "All seasons" if season is None else f"Season {season}"
    counts = count_home_wins(games, season)
    team, points = top_scoring_team(games, season)

    print(f"--- {label} ---")
    print(f"Games played:        {sum(counts.values())}")
    print(f"Home / away / ties:  {counts['home']} / {counts['away']} / {counts['tie']}")
    print(f"Home win %:          {home_win_pct(games, season):.1%}")
    print(f"Top scoring team:    {team} ({points} points)")
    print(f"Avg total points:    {average_total_points(games, season):.2f}")
    print()


def main():
    games = load_games(DATA_PATH)
    print_summary(games)
    print_summary(games, season=2025)


# This guard lets other files import our functions without running main()
if __name__ == "__main__":
    main()
