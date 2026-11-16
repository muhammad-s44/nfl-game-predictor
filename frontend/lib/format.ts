/** 0.594 -> "59.4%" (or "59%" with digits = 0) */
export const pct = (x: number, digits = 1) => `${(x * 100).toFixed(digits)}%`;

/** "2026-10-22" -> "Thu, Oct 22". Dates are calendar days, so format in UTC. */
export function gameDate(iso: string) {
  return new Date(`${iso}T00:00:00Z`).toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  });
}

/**
 * The Vegas line in words. nflverse's spread_line is the HOME team's expected
 * margin (positive = home favoured), the opposite sign of sportsbook notation.
 */
export function vegasLine(favorite: string | null, spread: number | null) {
  if (spread === null) return "No line yet";
  if (spread === 0 || favorite === null) return "Pick'em";
  return `${favorite} by ${Math.abs(spread)}`;
}

/** 7 -> "+7", -3 -> "−3" (real minus sign), 0 -> "0" */
export function signed(n: number) {
  if (n > 0) return `+${n}`;
  if (n < 0) return `−${Math.abs(n)}`;
  return "0";
}

export const record = (w: number, l: number, t = 0) => (t ? `${w}–${l}–${t}` : `${w}–${l}`);
