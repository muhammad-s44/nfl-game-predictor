// TypeScript mirrors of backend/app/schemas.py. If a field changes there,
// change it here too; the compiler then points at every page that uses it.

export type GamePrediction = {
  game_id: string;
  season: number;
  week: number;
  gameday: string; // "YYYY-MM-DD"
  home_team: string;
  away_team: string;
  home_win_prob: number;
  predicted_winner: string;
  spread_line: number | null;
  vegas_favorite: string | null;
  status: "scheduled" | "final";
  home_score: number | null;
  away_score: number | null;
  correct: boolean | null;
};

export type PredictionsResponse = {
  season: number;
  week: number;
  weeks: number[];
  results_through: string | null;
  games: GamePrediction[];
};

export type SeasonStats = {
  season: number;
  games: number;
  wins: number;
  losses: number;
  ties: number;
  points_for: number;
  points_against: number;
  point_diff: number;
  avg_points_for: number;
  avg_points_against: number;
  home_wins: number;
  home_losses: number;
  away_wins: number;
  away_losses: number;
};

export type GameResult = "W" | "L" | "T";

export type SeasonGame = {
  week: number;
  gameday: string;
  opponent: string;
  home_away: "home" | "away";
  points_for: number;
  points_against: number;
  result: GameResult;
};

export type RecentGame = SeasonGame & { game_id: string; season: number };

export type TeamResponse = {
  abbr: string;
  name: string;
  conference: string;
  division: string;
  season_stats: SeasonStats;
  season_games: SeasonGame[];
  recent_form: {
    games: RecentGame[];
    wins: number;
    losses: number;
    ties: number;
    avg_point_diff: number;
  };
};

export type TeamSummary = {
  abbr: string;
  name: string;
  conference: string;
  division: string;
  wins: number;
  losses: number;
  ties: number;
};

export type TeamsResponse = { season: number; teams: TeamSummary[] };

export type MethodAccuracy = { method: string; correct: number; accuracy: number };

export type SeasonAccuracy = {
  season: number;
  trained_on: string;
  games: number;
  games_remaining: number;
  methods: MethodAccuracy[];
};
