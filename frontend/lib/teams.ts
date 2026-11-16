// Team colours: [primary, secondary]. Shown only as a small two-tone swatch
// next to the abbreviation, never as a logo. Several primaries are very dark
// navy, so the swatch always shows both colours and has a faint ring.
export const TEAM_COLORS: Record<string, [string, string]> = {
  ARI: ["#97233F", "#FFB612"],
  ATL: ["#A71930", "#A5ACAF"],
  BAL: ["#241773", "#9E7C0C"],
  BUF: ["#00338D", "#C60C30"],
  CAR: ["#0085CA", "#BFC0BF"],
  CHI: ["#0B162A", "#C83803"],
  CIN: ["#FB4F14", "#000000"],
  CLE: ["#FF3C00", "#311D00"],
  DAL: ["#003594", "#869397"],
  DEN: ["#FB4F14", "#002244"],
  DET: ["#0076B6", "#B0B7BC"],
  GB: ["#203731", "#FFB612"],
  HOU: ["#03202F", "#A71930"],
  IND: ["#002C5F", "#A2AAAD"],
  JAX: ["#006778", "#D7A22A"],
  KC: ["#E31837", "#FFB81C"],
  LA: ["#003594", "#FFA300"],
  LAC: ["#0080C6", "#FFC20E"],
  LV: ["#A5ACAF", "#000000"],
  MIA: ["#008E97", "#FC4C02"],
  MIN: ["#4F2683", "#FFC62F"],
  NE: ["#002244", "#C60C30"],
  NO: ["#D3BC8D", "#101820"],
  NYG: ["#0B2265", "#A71930"],
  NYJ: ["#125740", "#FFFFFF"],
  PHI: ["#004C54", "#A5ACAF"],
  PIT: ["#FFB612", "#101820"],
  SEA: ["#002244", "#69BE28"],
  SF: ["#AA0000", "#B3995D"],
  TB: ["#D50A0A", "#B1BABF"],
  TEN: ["#4B92DB", "#C8102E"],
  WAS: ["#5A1414", "#FFB612"],
};

export const teamColors = (abbr: string): [string, string] =>
  TEAM_COLORS[abbr] ?? ["#8a857a", "#b5b0a4"];

/** "Kansas City Chiefs" -> ["Kansas City", "Chiefs"] for the italic headline word. */
export function splitTeamName(name: string): [string, string] {
  const i = name.lastIndexOf(" ");
  return i === -1 ? ["", name] : [name.slice(0, i), name.slice(i + 1)];
}
