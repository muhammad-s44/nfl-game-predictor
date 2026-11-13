"""The FastAPI app: three endpoints that read predictions from SQLite.

Run from the repo root (inside the virtual environment):
    python pipeline/build_db.py              # once, to build data/nfl.db
    uvicorn backend.app.main:app --reload    # then open http://localhost:8000/docs

Endpoints are plain `def` (not `async def`) because sqlite3 is blocking.
FastAPI runs plain `def` endpoints on a thread pool, so one slow query
doesn't freeze every other request.
"""

import sqlite3

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from . import queries
from .db import get_db
from .schemas import MethodAccuracy, PredictionsResponse, SeasonAccuracy, TeamResponse

app = FastAPI(
    title="NFL Game Predictor API",
    description="Logistic regression predictions for NFL games, served from SQLite.",
)

# CORS: browsers block a page on localhost:3000 from reading responses from
# localhost:8000 unless the API says that origin is allowed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/predictions", response_model=PredictionsResponse)
def get_predictions(
    week: int = Query(ge=1, le=18, description="Regular-season week (1-18)"),
    season: int | None = Query(None, description="Defaults to the latest predicted season"),
    conn: sqlite3.Connection = Depends(get_db),
):
    """Every predicted game in one week, with results for games already played."""
    if season is None:
        season = queries.latest_predicted_season(conn)
    games = queries.predictions_for_week(conn, season, week)
    if not games:
        raise HTTPException(404, f"No predictions for season {season}, week {week}")
    return {"season": season, "week": week, "games": games}


@app.get("/teams/{abbr}", response_model=TeamResponse)
def get_team(
    abbr: str,
    season: int | None = Query(None, description="Defaults to the team's latest season"),
    conn: sqlite3.Connection = Depends(get_db),
):
    """A team's regular-season stats and its last 5 games."""
    abbr = abbr.upper()
    team = queries.team_by_abbr(conn, abbr)
    if team is None:
        raise HTTPException(404, f"Unknown team '{abbr}'")
    if season is None:
        season = queries.latest_played_season(conn, abbr)
    stats = queries.season_stats(conn, abbr, season)
    if stats is None:
        raise HTTPException(404, f"No played games for {abbr} in season {season}")

    recent = queries.recent_games(conn, abbr, season, limit=5)
    diffs = [g["points_for"] - g["points_against"] for g in recent]
    recent_form = {
        "games": recent,
        "wins": sum(g["result"] == "W" for g in recent),
        "losses": sum(g["result"] == "L" for g in recent),
        "ties": sum(g["result"] == "T" for g in recent),
        "avg_point_diff": round(sum(diffs) / len(diffs), 1),
    }
    return {**team, "season_stats": stats, "recent_form": recent_form}


@app.get("/model/accuracy", response_model=list[SeasonAccuracy])
def get_model_accuracy(conn: sqlite3.Connection = Depends(get_db)):
    """The model vs always-pick-home vs the Vegas favorite, per test season.

    Each season is predicted by a model trained only on earlier seasons,
    so every number here is out-of-sample.
    """
    result = []
    for row in queries.accuracy_by_season(conn):
        n = row["games"]
        methods = [
            MethodAccuracy(method=name, correct=row[col], accuracy=round(row[col] / n, 4))
            for name, col in [("Logistic regression", "model_correct"),
                              ("Always pick home team", "home_correct"),
                              ("Vegas favorite", "vegas_correct")]
        ]
        result.append(SeasonAccuracy(
            season=row["season"],
            trained_on=f"{row['train_first']}-{row['train_last']}",
            games=n,
            games_remaining=row["games_remaining"],
            methods=methods,
        ))
    return result
