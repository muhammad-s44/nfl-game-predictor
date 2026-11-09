# Learning Guide

This guide walks through the project one stage at a time, in the same order as the git history. Read a stage, open the matching file, then check out that stage's commit (`git log --oneline` lists them) and run the code yourself.

For each function you'll find:
- **What** it does, in plain English
- **Why** it's built that way
- **Concepts** it uses (Python, pandas, ML)
- **Beginner mistakes** to watch for

---

## Stage 1: Plain Python (`src/explore.py`)

**Goal:** answer simple questions ("how often does the home team win?") with nothing but lists, dicts and loops. pandas does these same things in one line, but you can only explain pandas in an interview once you know what it does under the hood.

### The data in one paragraph

`data/games.csv` has one row per NFL game since 1999. The columns we use most are `season`, `week`, `gameday`, `home_team`, `away_team`, `home_score` and `away_score`. Games that haven't been played yet are in the file too, with **blank** scores. Every value that `csv.DictReader` reads is a **string**, even numbers.

### `load_games(path)`

**What:** opens the CSV, skips unplayed games, turns `home_score`, `away_score`, `season` and `week` into integers, and returns a list of dicts (one dict per game).

**Why:**
- Converting types *once, at load time* means every other function can do math without thinking about it. If the conversion lived in each function, you'd forget it somewhere.
- Unplayed games are skipped here so no later function ever sees a blank score.
- `with open(...) as f:` closes the file automatically, even if something crashes.

**Concepts:** `csv.DictReader` (each row becomes a dict keyed by the header line), `with` blocks (context managers), `int()` conversion, `continue` to skip a loop iteration.

**Beginner mistakes:**
- Forgetting `int()`. With strings, `"17" + "14"` is `"1714"`, and `"9" > "10"` is `True` because strings compare letter by letter.
- Calling `int("")` on an unplayed game, which crashes with `ValueError`. That's why the blank check comes *before* the conversion.
- Returning from inside the `for` loop by accident, which gives you back only one game.

### `filter_season(games, season=None)`

**What:** returns only the games from one season, or every game if no season is given.

**Why:** all the question functions take an optional `season`. Writing the filter once and reusing it is the DRY principle ("Don't Repeat Yourself"). If the filtering rule ever changes, you fix it in one place.

**Concepts:** default arguments (`season=None`), list comprehensions (`[g for g in games if ...]`), `is None` checks.

**Beginner mistakes:**
- Writing `if not season:` instead of `if season is None:`. That works here, but it would treat `0` as "no season". Using `is None` says exactly what you mean.
- Comparing `g["season"] == "2025"` (a string) against an int season. It's always `False`, so you get an empty list and no error message. This is the reason `load_games` converts `season`.

### `count_home_wins(games, season=None)`

**What:** loops through games and counts home wins, away wins and ties. Returns a dict like `{"home": 4144, "away": 3209, "tie": 16}`.

**Why:**
- **Ties are handled explicitly.** A naive `if home > away: wins += 1` quietly treats every tie as a home *loss*. There are 16 ties since 1999. That's a small number, but being explicit is a habit interviewers notice.
- Returning all three counts (not just home wins) lets `home_win_pct` reuse this function instead of looping again.

**Concepts:** `if / elif / else`, dicts as counters, `+=`.

**Beginner mistakes:**
- Using `>=` for a home win, which counts ties as home wins.
- Forgetting ties exist at all. They're rare in the NFL but real.

### `home_win_pct(games, season=None)`

**What:** home wins divided by games that had a winner (ties left out). Returns `None` if there are no decided games.

**Why:**
- **Ties are left out of the denominator.** The question is "when someone wins, how often is it the home team?" A tie answers neither way. (Another fair choice is counting a tie as half a win. What matters is picking a rule and stating it.)
- Returning `None` instead of crashing with `ZeroDivisionError` handles a season with no games, e.g. a typo like `season=2052`.

**Concepts:** division in Python 3 (`/` always gives a float), guard clauses (return early when the input is bad).

**Beginner mistakes:**
- Dividing by `len(games)`, which counts ties in the denominator.
- Using `//` (floor division), which turns `0.56` into `0`.

### `points_by_team(games, season=None)`

**What:** builds a dict of total points per team, adding points from **both** home and away games.

**Why:**
- Each game gives points to two teams, so each loop iteration updates two entries.
- `totals.get(team, 0)` returns 0 the first time we see a team, so we don't need to pre-fill the dict with every team.

**Concepts:** `dict.get(key, default)`, tuple unpacking (`home, away = ...`).

**Beginner mistakes:**
- Counting only home points. Every team's total comes out about half of what it should be, and nothing crashes, so it's easy to miss.
- `totals[team] += points` without `.get`, which raises `KeyError` the first time a team appears.
- **Data gotcha:** relocated teams have different codes (`STL`→`LA`, `SD`→`LAC`, `OAK`→`LV`), so all-seasons totals split those franchises in two. Stage 3 handles this for features.

### `top_scoring_team(games, season=None)`

**What:** returns `(team, points)` for the highest-scoring team.

**Why:** `max(totals, key=totals.get)` loops over the dict's keys (team names) but compares them by their *values* (points).

**Concepts:** `max` with a `key=` function, functions as values (`totals.get` is passed in, not called).

**Beginner mistakes:**
- `max(totals)` with no key returns the alphabetically last team (`"WAS"`), not the best one.
- `max(totals.values())` gives you the points but loses the team name.
- Across *all* seasons, this favors teams that existed for every season (HOU started in 2002). Points per game would be a fairer comparison. Good to mention if asked "what would you change?"

### `average_total_points(games, season=None)`

**What:** average of `home_score + away_score` across games.

**Why:** a generator expression inside `sum()` adds up the totals without building an extra list. We compute the total ourselves from the scores instead of trusting the `total` column, since our scores are already ints.

**Concepts:** generator expressions, `sum`, `len`.

**Beginner mistakes:** dividing by zero when a season has no games (handled by returning `None`).

### `print_summary` and `main`

**What:** `print_summary` prints every answer for one season (or all), and `main` calls it twice.

**Why `if __name__ == "__main__":`?** When you run `python3 src/explore.py`, Python sets `__name__` to `"__main__"`, so `main()` runs. When Stage 2 does `from explore import load_games`, `__name__` is `"explore"` and nothing prints. Without the guard, importing the file would print everything as a side effect.

**Concepts:** f-strings with format specs (`{x:.1%}` shows `0.564` as `56.4%`, `{x:.2f}` gives 2 decimals), the `__main__` guard.

### Stage 1 results

| | All seasons | 2025 |
|---|---|---|
| Games | 7,369 | 285 |
| Home / away / tie | 4144 / 3209 / 16 | 152 / 132 / 1 |
| Home win % | 56.4% | 53.5% |
| Top scoring team | NE (12,515) | LA (599) |
| Avg total points | 44.28 | 45.96 |

---

## Stage 2: pandas (`src/analysis.py`)

**Goal:** redo Stage 1 in pandas, check that both versions agree, then answer two new questions: *has home-field advantage shrunk?* and *which teams win most as underdogs?*

### Setting up: virtual environments and `requirements.txt`

A **virtual environment** (`.venv/`) is a private folder of installed packages for one project. It means this project's pandas version can't break another project, and `requirements.txt` lets anyone recreate the same setup with `pip install -r requirements.txt`. Versions are pinned with `==` so the code runs the same on another machine. `.venv/` is in `.gitignore` because you commit the *recipe* (`requirements.txt`), never the installed packages.

**Beginner mistakes:** forgetting to `source .venv/bin/activate` in a new terminal, which gives `ModuleNotFoundError: No module named 'pandas'`. Committing `.venv/` to git.

### The core pandas idea: vectorized operations

In Stage 1 we looped over games one at a time. In pandas you write an operation on a **whole column** and pandas runs the loop for you (in fast C code):

```python
df["home_score"] > df["away_score"]   # a Series of True/False, one per game
(df["home_score"] > df["away_score"]).sum()   # True counts as 1, so this counts home wins
```

A **DataFrame** is a table. A **Series** is one column of it, with an **index** (row labels).

### `load_games_df(path)`

**What:** `pd.read_csv` then `dropna` on the score columns, then convert scores to int.

**Why:** pandas reads blank cells as `NaN`. A column containing any `NaN` must be float (NaN is a float), which is why scores load as `17.0`. After the unplayed games are dropped we can safely `astype(int)`. Unlike `csv`, pandas already guessed that `season` and `week` are numbers.

**Beginner mistakes:** calling `astype(int)` *before* `dropna`, which fails with "cannot convert NaN to integer". Forgetting that `dropna` returns a *new* DataFrame (you must assign it back).

### `filter_season(df, season)`: boolean indexing

`df[df["season"] == season]` is **boolean indexing**. The inner part is a True/False Series, and the outer `df[...]` keeps only the True rows. It's the pandas version of the list comprehension in Stage 1.

### `count_home_wins`, `home_win_pct`, `average_total_points`

Same logic as Stage 1, but each count is a comparison followed by `.sum()`. We wrap results in `int(...)` because pandas returns numpy integers. They print the same, but `{"home": np.int64(4144)} == {"home": 4144}` comparisons and JSON output are cleaner with plain ints.

### `points_by_team(df)`: `groupby`

**What:** `df.groupby("home_team")["home_score"].sum()` means "split the rows by home team, then sum home_score within each group". We do the same for away teams, then add the two Series together.

**Why `add(..., fill_value=0)`?** Adding two Series lines them up by index (team name). If a team appeared only on one side, plain `+` would give `NaN` for it. `fill_value=0` treats the missing side as 0 points.

**Concepts:** split-apply-combine (`groupby`), index alignment, `sort_values`.

**Beginner mistake:** `home + away` without `fill_value`. That silently gives NaN for any team missing from one side. Index alignment is powerful but surprising.

### `check_matches_stage1`

**What:** asserts that the pandas answers equal the plain-Python answers.

**Why:** two independent implementations agreeing is strong evidence both are right. Floats are compared with a tolerance (`< 1e-9`) instead of `==`, because the two versions may add numbers in a different order and get rounding differences in the last digit.

### `home_win_pct_by_season(df)` and `compare_eras`

**What:** home win % per season, then the average before 2015 vs 2015 onward.

**Why the extra filters?**
- **Neutral-site games are excluded** (`location != "Home"`). The "home" team in a Super Bowl or a neutral international game has no real home advantage, so including them blurs the answer. This is why the overall number here differs slightly from Stage 1, and you should be able to explain that difference.
- **Ties are excluded**, same rule as Stage 1.
- **Only complete seasons** (up to the last Super Bowl in the data). A half-played season is mostly early-season games and isn't comparable.

**Concept:** `True/False` Series `.mean()` = fraction True. `groupby(...).mean()` gives that fraction per group.

**Finding:** home teams won **57.7%** of decided games in 1999–2014 vs **55.1%** in 2015–2025. 2020 (empty stadiums during COVID) was 50.4%, almost a coin flip, which is a nice natural experiment showing crowds matter. 2019 and 2021 were low too, so it isn't only fans. Home-field advantage has shrunk, but it hasn't disappeared.

### `add_underdog_columns`, `underdog_win_rates`, `overall_underdog_win_pct`

**The sign of `spread_line` (checked, not assumed):** in nflverse, `spread_line` is the **home team's expected margin**. Positive means the home team is favored. That is the *opposite* of how sportsbooks print lines ("KC -3" means KC is favored). Evidence from our data:
- Super Bowl LVI (LA @ CIN): `spread_line = -4.5`. The Rams, the away team, really were 4.5-point favorites, and CIN's moneyline was +160 (underdog).
- Super Bowl LIX (KC @ PHI): `-1.5`, and KC (away) was the favorite, at -120 on the moneyline.
- Across all games, `spread_line > 0` agrees with "the home moneyline is negative (home is the favorite)" 98% of the time, and `spread_line` correlates positively (+0.43) with `result` (home minus away).

**What the functions do:**
- `add_underdog_columns` drops pick'em games (`spread_line == 0`, no underdog), names the underdog, and marks whether they won. `Series.where(cond, other)` keeps a value where `cond` is True and takes `other` where it's False. It's a vectorized if/else.
- `underdog_win_rates` groups by underdog and uses `.agg(games="count", wins="sum")` to compute two columns at once. Teams with fewer than 20 underdog games are dropped, because a 3-for-5 team would show 60% and top the list on pure luck. That's **small-sample noise**.

**`.copy()`:** `add_underdog_columns` filters and then adds columns. Without `.copy()`, pandas may warn that you're modifying a *view* of the original data (`SettingWithCopyWarning`). Copying makes it clear we own a new DataFrame.

**Finding:** underdogs win **33.4%** of games. Pittsburgh is the best underdog by far (49.7% over 167 games). Cleveland (24.8%) and Detroit (25.7%) are the worst.

**Beginner mistakes:**
- Assuming the sportsbook sign convention and getting every favorite backwards. **Always check a sign convention against games whose answer you know.**
- Counting a tie as an underdog win (`result <= 0`).
- Ranking teams without a minimum sample size.
