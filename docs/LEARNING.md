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
