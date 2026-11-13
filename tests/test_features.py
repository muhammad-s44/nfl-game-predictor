"""Automated checks that features.py never leaks future information.

Run from the repo root (inside the virtual environment):
    python tests/test_features.py
(pytest also finds these tests if you install it, but it isn't required.)
"""

import os
import sys

import numpy as np
import pandas as pd

# Let this file import from src/ even though it lives in tests/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from analysis import DATA_PATH, load_games_df, load_schedule_df  # noqa: E402
from features import FEATURE_COLUMNS, FRANCHISE, build_features  # noqa: E402

GAMES = load_games_df(DATA_PATH)            # played games only
SCHEDULE = load_schedule_df(DATA_PATH)      # played + upcoming games
FEATURES = build_features(GAMES)
SCHEDULE_FEATURES = build_features(SCHEDULE)
UNPLAYED = SCHEDULE_FEATURES["home_score"].isna()


def scramble_from(df, cutoff, seed=0):
    """Copy df with random scores for every game on or after `cutoff`."""
    df = df.copy()
    future = df["gameday"] >= cutoff
    rng = np.random.default_rng(seed)
    df.loc[future, "home_score"] = rng.integers(0, 60, future.sum())
    df.loc[future, "away_score"] = rng.integers(0, 60, future.sum())
    df["result"] = df["home_score"] - df["away_score"]
    df["total"] = df["home_score"] + df["away_score"]
    return df


def test_future_results_do_not_change_features():
    """The core leakage check: rewrite the future, the present must not move.

    If a game's features depended on its own score or any later score,
    scrambling those scores would change them. Games ON the cutoff date
    have their own scores scrambled too, which catches self-leakage.
    """
    for cutoff in ["2005-09-11", "2018-12-02", "2025-09-04", "2025-11-16"]:
        scrambled = build_features(scramble_from(GAMES, cutoff))
        upto = FEATURES["gameday"] <= pd.Timestamp(cutoff)
        assert upto.sum() > 0
        pd.testing.assert_frame_equal(
            FEATURES.loc[upto, FEATURE_COLUMNS],
            scrambled.loc[upto, FEATURE_COLUMNS],
        )
        # Sanity check the test itself: later games SHOULD change, or the
        # scramble did nothing and the test above proves nothing.
        later = FEATURES["gameday"] > pd.Timestamp(cutoff)
        assert not FEATURES.loc[later, FEATURE_COLUMNS].equals(
            scrambled.loc[later, FEATURE_COLUMNS])


def slow_team_features(team, before, season):
    """Recompute one team's features the obvious way, with a plain filter.

    This is deliberately simple (and slow) so it is easy to trust.
    """
    g = GAMES.copy()
    g["home_team"] = g["home_team"].replace(FRANCHISE)
    g["away_team"] = g["away_team"].replace(FRANCHISE)
    g["gameday"] = pd.to_datetime(g["gameday"])
    past = g[((g["home_team"] == team) | (g["away_team"] == team))
             & (g["gameday"] < before)].sort_values("gameday")

    is_home = past["home_team"] == team
    pf = past["home_score"].where(is_home, past["away_score"])
    pa = past["away_score"].where(is_home, past["home_score"])

    this_season = past["season"] == season
    wins = (pf[this_season] > pa[this_season]).sum()
    ties = (pf[this_season] == pa[this_season]).sum()
    played = this_season.sum()
    win_pct = (wins + 0.5 * ties) / played if played else 0.5
    return pf.tail(3).mean(), pa.tail(3).mean(), win_pct


def test_features_match_slow_recomputation():
    """Spot-check 150 random games against the brute-force version."""
    sample = FEATURES.dropna(subset=FEATURE_COLUMNS).sample(150, random_state=1)
    for _, game in sample.iterrows():
        for side in ("home", "away"):
            team = FRANCHISE.get(game[f"{side}_team"], game[f"{side}_team"])
            pf, pa, win_pct = slow_team_features(team, game["gameday"], game["season"])
            assert np.isclose(game[f"{side}_pf_last3"], pf), game["game_id"]
            assert np.isclose(game[f"{side}_pa_last3"], pa), game["game_id"]
            assert np.isclose(game[f"{side}_win_pct"], win_pct), game["game_id"]


def test_week_one_win_pct_is_neutral():
    """Nobody has a record before their first game of the season."""
    week1 = FEATURES[(FEATURES["week"] == 1) & (FEATURES["game_type"] == "REG")]
    assert (week1["home_win_pct"] == 0.5).all()
    assert (week1["away_win_pct"] == 0.5).all()


def test_unplayed_games_do_not_change_played_features():
    """Adding the upcoming schedule must not move any played game's features.

    An unplayed game has no score, so it is not part of any team's history.
    """
    assert UNPLAYED.sum() > 0, "no unplayed games in the data to test with"
    played = SCHEDULE_FEATURES[~UNPLAYED].set_index("game_id")
    expected = FEATURES.set_index("game_id").loc[played.index]
    pd.testing.assert_frame_equal(played[FEATURE_COLUMNS], expected[FEATURE_COLUMNS],
                                  check_dtype=False)


def test_unplayed_games_use_only_played_history():
    """Each upcoming game's features come from played games only.

    A game two weeks away must not count next week's (unplayed) game as a
    loss, or as a game played, or as one of the "last 3" games.
    """
    upcoming = SCHEDULE_FEATURES[UNPLAYED]
    for _, game in upcoming.iterrows():
        for side in ("home", "away"):
            team = FRANCHISE.get(game[f"{side}_team"], game[f"{side}_team"])
            pf, pa, win_pct = slow_team_features(team, game["gameday"], game["season"])
            assert np.isclose(game[f"{side}_pf_last3"], pf), game["game_id"]
            assert np.isclose(game[f"{side}_pa_last3"], pa), game["game_id"]
            assert np.isclose(game[f"{side}_win_pct"], win_pct), game["game_id"]


if __name__ == "__main__":
    tests = [test_future_results_do_not_change_features,
             test_features_match_slow_recomputation,
             test_week_one_win_pct_is_neutral,
             test_unplayed_games_do_not_change_played_features,
             test_unplayed_games_use_only_played_history]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print("No data leakage detected.")
