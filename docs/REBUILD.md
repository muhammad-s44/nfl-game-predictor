# Rebuild Exercises

Redo each piece **from a blank file, without looking at the solution**. Then run the check. If it fails, compare against the real file, close it again, and redo the exercise from scratch the next day.

**Setup:** put your attempts in a `practice/` folder (it's in `.gitignore`, so it won't clutter the project), and run everything from the repo root with the virtual environment active. Each check script starts with this so it can import the project's code:

```python
import sys
sys.path.insert(0, "src")
```

Suggested order: 1 → 2 → 3 → 4 → 5 → 6 → 7. Time yourself. In an interview you may be asked to write something like Exercise 1 in under 10 minutes.

---

## Exercise 1: `points_by_team` in plain Python (no pandas)

Write `points_by_team(games, season=None)` in `practice/ex1.py`. It takes the list of dicts from `explore.load_games` and returns `{team: total_points}`, counting **both** home and away points.

**Check:**

```python
import sys
sys.path.insert(0, "src"); sys.path.insert(0, "practice")
import explore
from ex1 import points_by_team

games = explore.load_games("data/games.csv")
assert points_by_team(games) == explore.points_by_team(games)
assert points_by_team(games, 2025)["LA"] == 599
assert points_by_team(games)["NE"] == 12515
print("Exercise 1 passed")
```

**Common failure:** totals are about half of what they should be → you only counted home games.

---

## Exercise 2: `home_win_pct` with ties handled

Write `count_home_wins` and `home_win_pct` in plain Python. Ties must not count as wins or losses.

**Check:** all seasons gives **56.4%** (4144 home, 3209 away, 16 ties). 2025 gives **53.5%** (152 / 132 / 1).

```python
from ex2 import home_win_pct
assert round(home_win_pct(games), 3) == 0.564
assert round(home_win_pct(games, 2025), 3) == 0.535
```

**Common failure:** 56.2% → you divided by all games, including ties.

---

## Exercise 3: the same two questions in pandas

In `practice/ex3.py`, load the CSV with `pd.read_csv`, drop unplayed games, and compute points by team using `groupby` (no loops).

**Check:**

```python
import pandas as pd
from ex3 import points_by_team   # should return a Series
import explore

games = explore.load_games("data/games.csv")
expected = explore.points_by_team(games)
mine = points_by_team(pd.read_csv("data/games.csv").dropna(subset=["home_score"]))
assert {team: int(pts) for team, pts in mine.items()} == expected
print("Exercise 3 passed")
```

---

## Exercise 4: underdog win rate

Using `spread_line` (positive = **home** favored), compute the fraction of non-pick'em games won by the underdog. Ties are not underdog wins.

**Check:** the answer is **33.4%**. If you get about 66.6%, your sign is backwards. Go back to the Stage 2 notes on the `spread_line` convention.

---

## Exercise 5: rebuild one feature, `pa_last3`

Write a function that returns, for every game, the **home team's average points allowed over its previous 3 games** (any season, home or away, fewer than 3 if that's all there is). Remember the relocation map `{"STL": "LA", "SD": "LAC", "OAK": "LV"}`.

Hints, only if stuck: two rows per game → sort by team and date → `groupby` + `shift(1)` + `rolling(3, min_periods=1)` → merge back.

**Check (correctness):**

```python
import numpy as np
from analysis import load_games_df, DATA_PATH
from features import build_features
from ex5 import home_pa_last3     # returns a DataFrame with game_id, home_pa_last3

df = load_games_df(DATA_PATH)
expected = build_features(df)[["game_id", "home_pa_last3"]]
mine = home_pa_last3(df)
merged = expected.merge(mine, on="game_id", suffixes=("", "_mine"))
assert len(merged) == len(expected)
assert np.allclose(merged["home_pa_last3"], merged["home_pa_last3_mine"], equal_nan=True)
print("Exercise 5 passed")
```

**Check (no leakage):** copy `scramble_from` and the first test from `tests/test_features.py`, and point them at your function. Then delete your `shift(1)` and confirm the test **fails**. If it still passes, your test is broken.

---

## Exercise 6: season win % to date

Add `home_win_pct`: the home team's win percentage this season **before** this game (tie = 0.5 win, 0.5 when no games yet).

**Check:** same pattern as Exercise 5, comparing against `build_features(df)["home_win_pct"]`. Also every regular-season week 1 value must be exactly 0.5.

---

## Exercise 7: retrain the model

In `practice/ex7.py`, starting from `build_features(load_games_df(DATA_PATH))`:

1. Keep regular-season games, drop ties, drop rows with missing features.
2. Target: `home_win` = 1 if the home team won.
3. Features: `pf_last3_diff, pa_last3_diff, win_pct_diff, rest_diff, div_game`.
4. Train on seasons 2018–2024, test on 2025.
5. `StandardScaler` + `LogisticRegression` in a pipeline.
6. Print accuracy for the model, "always home" and "Vegas favorite".

**Check:** you should get exactly these (the model has no randomness, so the numbers reproduce):

| Method | Correct | Accuracy |
|---|---|---|
| Always home | 146/271 | 53.9% |
| Logistic regression | 161/271 | 59.4% |
| Vegas favorite | 177/271 | 65.3% |

**If your numbers differ:**
- 272 test games → you didn't drop the 2025 tie.
- Vegas around 35% → `spread_line` sign is backwards.
- Model accuracy way above 65% → you probably used `home_score`, `result` or `spread_line` as a feature (leakage!).
- Slightly different model accuracy → check that you trained on 2018–**2024** (`range(2018, 2025)`) and scaled inside a pipeline.

---

## Stretch exercises (no answer key, so explain your result in a sentence)

- Add `spread_line` as a sixth feature. Does the model now beat Vegas, or just copy it? Look at the coefficients.
- Walk-forward validation: train on 2011–2017 → test 2018, train on 2012–2018 → test 2019, and so on. Report the average accuracy. Is 59.4% typical, or was 2025 lucky?
- Change the rolling window from 3 to 5 games. Better or worse? Why might that be?
