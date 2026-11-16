import Link from "next/link";
import type { GamePrediction } from "@/lib/types";
import { gameDate, pct, vegasLine } from "@/lib/format";
import { Card, TeamSwatch } from "./ui";

/** One game: both teams, the model's win probabilities, the Vegas line, and the result if played. */
export function GameCard({ game }: { game: GamePrediction }) {
  const homeProb = game.home_win_prob;
  const awayProb = 1 - homeProb;
  const final = game.status === "final";

  return (
    <Card className="flex flex-col gap-5 p-5 sm:p-6">
      <div className="flex items-center justify-between gap-3 text-xs">
        <span className="uppercase tracking-[0.18em] text-fg-3">{gameDate(game.gameday)}</span>
        <StatusBadge game={game} />
      </div>

      <div className="flex flex-col gap-3">
        <TeamRow
          abbr={game.away_team}
          side="away"
          prob={awayProb}
          score={game.away_score}
          picked={game.predicted_winner === game.away_team}
          final={final}
        />
        <TeamRow
          abbr={game.home_team}
          side="home"
          prob={homeProb}
          score={game.home_score}
          picked={game.predicted_winner === game.home_team}
          final={final}
        />
      </div>

      <ProbabilityBar game={game} />

      <p className="text-sm text-fg-3">
        Vegas: <span className="text-fg-2">{vegasLine(game.vegas_favorite, game.spread_line)}</span>
      </p>
    </Card>
  );
}

function TeamRow({
  abbr,
  side,
  prob,
  score,
  picked,
  final,
}: {
  abbr: string;
  side: "home" | "away";
  prob: number;
  score: number | null;
  picked: boolean;
  final: boolean;
}) {
  return (
    <div className="flex items-center gap-3">
      <TeamSwatch abbr={abbr} />
      <Link href={`/teams/${abbr}`} className="text-2xl font-semibold tracking-tight text-fg hover:text-accent">
        {abbr}
      </Link>
      <span className="text-xs text-fg-3">{side === "home" ? "home" : "away"}</span>
      {picked && (
        <span className="rounded-full bg-accent px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-accent-ink">
          Pick
        </span>
      )}
      <span className="ml-auto flex items-baseline gap-3">
        {final && score !== null && <span className="font-serif text-3xl leading-none text-fg">{score}</span>}
        <span className={`tabular-nums ${final ? "text-sm text-fg-3" : picked ? "text-lg text-fg" : "text-lg text-fg-3"}`}>
          {pct(prob, 0)}
        </span>
      </span>
    </div>
  );
}

/**
 * A split bar: away share on the left, home share on the right, with a 2px
 * gap between them. The model's pick is the bright side.
 */
function ProbabilityBar({ game }: { game: GamePrediction }) {
  const home = game.home_win_prob;
  const homePicked = home > 0.5;
  return (
    <div
      role="img"
      aria-label={`Model: ${game.away_team} ${pct(1 - home, 0)}, ${game.home_team} ${pct(home, 0)}`}
      className="flex h-2 w-full gap-[2px]"
    >
      <div
        className={`h-full rounded-l-full ${homePicked ? "bg-fg/15" : "bg-accent"}`}
        style={{ width: `${(1 - home) * 100}%` }}
      />
      <div
        className={`h-full rounded-r-full ${homePicked ? "bg-accent" : "bg-fg/15"}`}
        style={{ width: `${home * 100}%` }}
      />
    </div>
  );
}

function StatusBadge({ game }: { game: GamePrediction }) {
  if (game.status === "scheduled") return <span className="text-fg-3">Upcoming</span>;
  if (game.correct === null) return <span className="text-fg-3">Final · Tie</span>;
  return game.correct ? (
    <span className="rounded-full bg-accent/15 px-2.5 py-1 font-medium text-accent">✓ Called it</span>
  ) : (
    <span className="rounded-full bg-card-2 px-2.5 py-1 text-fg-2 ring-1 ring-line">✗ Missed</span>
  );
}
