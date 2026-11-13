"""API tests: build a fresh database, call each endpoint, check the answers.

Where possible, the expected values come from somewhere other than the SQL
being tested (pandas on the raw CSV, or results.md), so a wrong query
can't pass by agreeing with itself.

Run from the repo root:  python -m pytest backend/tests -v
"""

import sqlite3

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from pipeline.build_db import CSV_PATH, build


@pytest.fixture(scope="session")
def db_file(tmp_path_factory):
    """Build the database once for the whole test run, in a temp folder."""
    path = tmp_path_factory.mktemp("db") / "nfl.db"
    build(db_path=path)
    return path


@pytest.fixture
def client(db_file, monkeypatch):
    monkeypatch.setenv("NFL_DB_PATH", str(db_file))
    return TestClient(app)


@pytest.fixture(scope="session")
def csv():
    return pd.read_csv(CSV_PATH)


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


# ---------- /predictions ----------

def test_predictions_cover_every_regular_season_game_in_the_week(client, csv):
    body = client.get("/predictions", params={"season": 2025, "week": 7}).json()
    expected = csv[(csv["season"] == 2025) & (csv["week"] == 7) & (csv["game_type"] == "REG")]
    assert {g["game_id"] for g in body["games"]} == set(expected["game_id"])


def test_prediction_fields_are_consistent(client):
    games = client.get("/predictions", params={"season": 2025, "week": 7}).json()["games"]
    for g in games:
        assert 0 < g["home_win_prob"] < 1
        expected_pick = g["home_team"] if g["home_win_prob"] > 0.5 else g["away_team"]
        assert g["predicted_winner"] == expected_pick
        assert g["status"] == "final"
        if g["home_score"] != g["away_score"]:
            actual_winner = g["home_team"] if g["home_score"] > g["away_score"] else g["away_team"]
            assert g["correct"] == (g["predicted_winner"] == actual_winner)


def test_predictions_default_to_latest_season_and_show_unplayed_games(client, csv):
    body = client.get("/predictions", params={"week": 18}).json()
    assert body["season"] == csv["season"].max()
    assert all(g["status"] == "scheduled" and g["correct"] is None for g in body["games"])


def test_predictions_errors(client):
    assert client.get("/predictions", params={"week": 0}).status_code == 422
    assert client.get("/predictions", params={"week": 19}).status_code == 422
    assert client.get("/predictions").status_code == 422  # week is required
    # 2010 was never predicted (only 2025 and 2026 are test seasons)
    assert client.get("/predictions", params={"season": 2010, "week": 1}).status_code == 404


# ---------- /teams/{abbr} ----------

def pandas_record(csv, team, season):
    """Wins, losses, points for/against the obvious way, straight from the CSV."""
    g = csv[(csv["season"] == season) & (csv["game_type"] == "REG") & csv["home_score"].notna()]
    home, away = g[g["home_team"] == team], g[g["away_team"] == team]
    pf = home["home_score"].sum() + away["away_score"].sum()
    pa = home["away_score"].sum() + away["home_score"].sum()
    wins = (home["home_score"] > home["away_score"]).sum() + (away["away_score"] > away["home_score"]).sum()
    losses = (home["home_score"] < home["away_score"]).sum() + (away["away_score"] < away["home_score"]).sum()
    return int(wins), int(losses), int(pf), int(pa)


@pytest.mark.parametrize("team", ["KC", "PIT", "LV"])
def test_team_season_stats_match_pandas(client, csv, team):
    stats = client.get(f"/teams/{team}", params={"season": 2025}).json()["season_stats"]
    wins, losses, pf, pa = pandas_record(csv, team, 2025)
    assert (stats["wins"], stats["losses"]) == (wins, losses)
    assert (stats["points_for"], stats["points_against"]) == (pf, pa)
    assert stats["home_wins"] + stats["away_wins"] == stats["wins"]


def test_team_recent_form(client):
    form = client.get("/teams/kc").json()["recent_form"]  # lowercase works too
    games = form["games"]
    assert len(games) == 5
    assert [g["gameday"] for g in games] == sorted((g["gameday"] for g in games), reverse=True)
    for g in games:
        expected = "W" if g["points_for"] > g["points_against"] else (
            "L" if g["points_for"] < g["points_against"] else "T")
        assert g["result"] == expected
    assert form["wins"] + form["losses"] + form["ties"] == 5


def test_relocated_team_history_is_under_current_code(client):
    """The Raiders played as OAK in 2019; that season belongs to LV."""
    assert client.get("/teams/LV", params={"season": 2019}).json()["season_stats"]["games"] == 16


def test_team_errors(client, db_file):
    assert client.get("/teams/XYZ").status_code == 404
    assert client.get("/teams/KC", params={"season": 1990}).status_code == 404
    # SQL injection attempt: placeholders make this just an unknown team name
    assert client.get("/teams/KC'; DROP TABLE games;--").status_code == 404
    conn = sqlite3.connect(db_file)
    assert conn.execute("SELECT COUNT(*) FROM games").fetchone()[0] > 0
    conn.close()


# ---------- /model/accuracy ----------

def test_accuracy_2025_matches_results_md(client):
    """The SQL must reproduce src/model.py's numbers (see results.md)."""
    seasons = {s["season"]: s for s in client.get("/model/accuracy").json()}
    s2025 = seasons[2025]
    assert s2025["trained_on"] == "2018-2024"
    assert s2025["games"] == 271 and s2025["games_remaining"] == 0
    correct = {m["method"]: m["correct"] for m in s2025["methods"]}
    assert correct == {"Logistic regression": 161, "Always pick home team": 146, "Vegas favorite": 177}


def test_accuracy_current_season_is_trained_only_on_the_past(client, csv):
    latest = int(csv["season"].max())
    s = {s["season"]: s for s in client.get("/model/accuracy").json()}[latest]
    assert s["trained_on"] == f"2018-{latest - 1}"
    assert s["games_remaining"] > 0


# ---------- missing database ----------

def test_missing_database_returns_503(monkeypatch, tmp_path):
    monkeypatch.setenv("NFL_DB_PATH", str(tmp_path / "nope.db"))
    assert TestClient(app).get("/model/accuracy").status_code == 503
