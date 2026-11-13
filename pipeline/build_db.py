"""Build data/nfl.db: games, teams, and model predictions in SQLite.

This is the offline step. It does the slow work (features + training) once,
so the API only has to look things up. Re-run it whenever games.csv changes:
    python pipeline/build_db.py

It builds the database from scratch every time, into a temporary file that
replaces the old one only when everything succeeded. The API never sees a
half-built database.
"""

import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from analysis import load_schedule_df  # noqa: E402
from features import FRANCHISE, build_features  # noqa: E402
from model import MODEL_FEATURES, TRAIN_SEASONS, coefficient_table, prepare_games, train_model  # noqa: E402

CSV_PATH = REPO / "data" / "games.csv"
DB_PATH = REPO / "data" / "nfl.db"
SCHEMA_PATH = REPO / "backend" / "schema.sql"

TRAIN_FIRST = min(TRAIN_SEASONS)  # 2018
# Each test season gets its own model, trained only on the seasons before it.
TEST_SEASONS = [2025, 2026]

# (abbr, name, conference, division). Codes match nflverse.
TEAMS = [
    ("BUF", "Buffalo Bills", "AFC", "AFC East"),
    ("MIA", "Miami Dolphins", "AFC", "AFC East"),
    ("NE", "New England Patriots", "AFC", "AFC East"),
    ("NYJ", "New York Jets", "AFC", "AFC East"),
    ("BAL", "Baltimore Ravens", "AFC", "AFC North"),
    ("CIN", "Cincinnati Bengals", "AFC", "AFC North"),
    ("CLE", "Cleveland Browns", "AFC", "AFC North"),
    ("PIT", "Pittsburgh Steelers", "AFC", "AFC North"),
    ("HOU", "Houston Texans", "AFC", "AFC South"),
    ("IND", "Indianapolis Colts", "AFC", "AFC South"),
    ("JAX", "Jacksonville Jaguars", "AFC", "AFC South"),
    ("TEN", "Tennessee Titans", "AFC", "AFC South"),
    ("DEN", "Denver Broncos", "AFC", "AFC West"),
    ("KC", "Kansas City Chiefs", "AFC", "AFC West"),
    ("LV", "Las Vegas Raiders", "AFC", "AFC West"),
    ("LAC", "Los Angeles Chargers", "AFC", "AFC West"),
    ("DAL", "Dallas Cowboys", "NFC", "NFC East"),
    ("NYG", "New York Giants", "NFC", "NFC East"),
    ("PHI", "Philadelphia Eagles", "NFC", "NFC East"),
    ("WAS", "Washington Commanders", "NFC", "NFC East"),
    ("CHI", "Chicago Bears", "NFC", "NFC North"),
    ("DET", "Detroit Lions", "NFC", "NFC North"),
    ("GB", "Green Bay Packers", "NFC", "NFC North"),
    ("MIN", "Minnesota Vikings", "NFC", "NFC North"),
    ("ATL", "Atlanta Falcons", "NFC", "NFC South"),
    ("CAR", "Carolina Panthers", "NFC", "NFC South"),
    ("NO", "New Orleans Saints", "NFC", "NFC South"),
    ("TB", "Tampa Bay Buccaneers", "NFC", "NFC South"),
    ("ARI", "Arizona Cardinals", "NFC", "NFC West"),
    ("LA", "Los Angeles Rams", "NFC", "NFC West"),
    ("SF", "San Francisco 49ers", "NFC", "NFC West"),
    ("SEA", "Seattle Seahawks", "NFC", "NFC West"),
]

GAME_COLUMNS = ["game_id", "season", "week", "game_type", "gameday",
                "home_team", "away_team", "home_score", "away_score",
                "spread_line", "home_rest", "away_rest", "div_game"]


def to_sql_value(value):
    """pandas uses NaN for missing values and numpy number types;
    sqlite3 wants None and plain Python ints/floats."""
    if value is None or value != value:  # NaN is the only value not equal to itself
        return None
    if hasattr(value, "item"):  # numpy scalar -> Python scalar
        return value.item()
    return value


def insert_games(conn, schedule):
    games = schedule[GAME_COLUMNS].copy()
    games["home_team"] = games["home_team"].replace(FRANCHISE)
    games["away_team"] = games["away_team"].replace(FRANCHISE)
    rows = [tuple(to_sql_value(v) for v in row)
            for row in games.itertuples(index=False)]
    # The ? placeholders are filled in by sqlite3, never pasted into the SQL
    # string. That is what protects against SQL injection.
    placeholders = ", ".join("?" for _ in GAME_COLUMNS)
    conn.executemany(
        f"INSERT INTO games ({', '.join(GAME_COLUMNS)}) VALUES ({placeholders})", rows)
    return len(rows)


def train_and_predict(conn, features, test_season):
    """Train on seasons before test_season, predict every test_season REG game."""
    played = features[features["home_score"].notna()]
    train = prepare_games(played)
    train = train[train["season"].between(TRAIN_FIRST, test_season - 1)]
    model = train_model(train)

    to_predict = features[(features["season"] == test_season)
                          & (features["game_type"] == "REG")]
    to_predict = to_predict.dropna(subset=MODEL_FEATURES)
    # predict_proba returns [[P(away win), P(home win)], ...]; column 1 is home
    home_win_prob = model.predict_proba(to_predict[MODEL_FEATURES])[:, 1]

    coefs = {feature: round(float(c), 4) for feature, c in coefficient_table(model)}
    cursor = conn.execute(
        """INSERT INTO model_runs
               (created_at, train_first, train_last, test_season, train_games, coefficients)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (datetime.now(timezone.utc).isoformat(timespec="seconds"),
         TRAIN_FIRST, test_season - 1, test_season, len(train), json.dumps(coefs)))
    run_id = cursor.lastrowid  # the run_id SQLite just generated

    conn.executemany(
        "INSERT INTO predictions (game_id, run_id, home_win_prob) VALUES (?, ?, ?)",
        [(game_id, run_id, float(p)) for game_id, p in zip(to_predict["game_id"], home_win_prob)])
    return len(train), len(to_predict)


def build(db_path=DB_PATH, csv_path=CSV_PATH):
    db_path = Path(db_path)
    tmp_path = db_path.with_suffix(".tmp")
    tmp_path.unlink(missing_ok=True)

    schedule = load_schedule_df(csv_path)
    features = build_features(schedule)

    conn = sqlite3.connect(tmp_path)
    try:
        conn.executescript(SCHEMA_PATH.read_text())
        conn.executemany("INSERT INTO teams VALUES (?, ?, ?, ?)", TEAMS)
        n_games = insert_games(conn, schedule)
        print(f"games: {n_games} rows")
        for season in TEST_SEASONS:
            n_train, n_pred = train_and_predict(conn, features, season)
            print(f"{season} model: trained on {n_train} games, predicted {n_pred}")
        conn.commit()
    finally:
        conn.close()
    os.replace(tmp_path, db_path)  # atomic swap: old DB until this line, new DB after
    print(f"saved {db_path.relative_to(REPO) if db_path.is_relative_to(REPO) else db_path}")


if __name__ == "__main__":
    build()
