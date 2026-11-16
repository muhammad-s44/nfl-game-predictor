import type {
  PredictionsResponse,
  SeasonAccuracy,
  TeamResponse,
  TeamsResponse,
} from "./types";

// Where the FastAPI server lives. These calls run on the Next.js server
// (server components), not in the browser, so this never reaches users.
const API_URL = process.env.API_URL ?? "http://127.0.0.1:8000";

// How long to wait for the API before showing the error page. Locally the API
// answers instantly, so 5 seconds. In production the API runs on Render's free
// plan, which sleeps after ~15 idle minutes and takes up to about a minute to
// wake, so wait longer there. Override with the API_TIMEOUT_MS variable.
const TIMEOUT_MS =
  Number(process.env.API_TIMEOUT_MS) || (process.env.NODE_ENV === "production" ? 75_000 : 5_000);

export class ApiError extends Error {}

/** GET a JSON endpoint. Returns null for a 404, throws for anything else. */
async function get<T>(path: string, params: Record<string, string | number | undefined> = {}) {
  const url = new URL(path, API_URL);
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined) url.searchParams.set(key, String(value));
  }

  let res: Response;
  try {
    // Give up after TIMEOUT_MS, so a hung API shows the error page instead
    // of leaving the page loading forever.
    res = await fetch(url, { signal: AbortSignal.timeout(TIMEOUT_MS) });
  } catch {
    throw new ApiError(`Can't reach the API at ${API_URL}. Is uvicorn running?`);
  }
  if (res.status === 404) return null;
  if (!res.ok) throw new ApiError(`API error ${res.status} on ${url.pathname}`);
  return (await res.json()) as T;
}

export const getPredictions = (week?: number, season?: number) =>
  get<PredictionsResponse>("/predictions", { week, season });

export const getTeams = (season?: number) => get<TeamsResponse>("/teams", { season });

export const getTeam = (abbr: string, season?: number) =>
  get<TeamResponse>(`/teams/${encodeURIComponent(abbr)}`, { season });

export const getAccuracy = async () => (await get<SeasonAccuracy[]>("/model/accuracy")) ?? [];
