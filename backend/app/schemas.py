"""The shape of every JSON response, written as Pydantic models.

FastAPI uses these to (1) check that each response really has these fields
and types, and (2) document them at http://localhost:8000/docs. The
frontend's TypeScript types will mirror these classes.
"""

from typing import Literal

from pydantic import BaseModel


# ---------- GET /predictions ----------

class GamePrediction(BaseModel):
    game_id: str
    season: int
    week: int
    gameday: str
    home_team: str
    away_team: str
    home_win_prob: float          # model's probability that the home team wins
    predicted_winner: str
    spread_line: float | None     # home team's expected margin; None = no line yet
    vegas_favorite: str | None    # None = no line yet, or a pick'em (spread 0)
    status: Literal["scheduled", "final"]
    home_score: int | None
    away_score: int | None
    correct: bool | None          # None until played (and for ties)


class PredictionsResponse(BaseModel):
    season: int
    week: int
    games: list[GamePrediction]


# ---------- GET /teams/{abbr} ----------

class SeasonStats(BaseModel):
    season: int
    games: int
    wins: int
    losses: int
    ties: int
    points_for: int
    points_against: int
    point_diff: int
    avg_points_for: float
    avg_points_against: float
    home_wins: int
    home_losses: int
    away_wins: int
    away_losses: int


class RecentGame(BaseModel):
    game_id: str
    season: int
    week: int
    gameday: str
    opponent: str
    home_away: Literal["home", "away"]
    points_for: int
    points_against: int
    result: Literal["W", "L", "T"]


class RecentForm(BaseModel):
    games: list[RecentGame]       # newest first
    wins: int
    losses: int
    ties: int
    avg_point_diff: float


class TeamResponse(BaseModel):
    abbr: str
    name: str
    conference: str
    division: str
    season_stats: SeasonStats
    recent_form: RecentForm


# ---------- GET /model/accuracy ----------

class MethodAccuracy(BaseModel):
    method: str
    correct: int
    accuracy: float               # 0.594 means 59.4%


class SeasonAccuracy(BaseModel):
    season: int
    trained_on: str               # e.g. "2018-2024"
    games: int                    # played, non-tie games scored
    games_remaining: int          # predicted games not played yet
    methods: list[MethodAccuracy]
