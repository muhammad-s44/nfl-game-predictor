import { Suspense } from "react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getTeam } from "@/lib/api";
import { gameDate, record, signed } from "@/lib/format";
import { splitTeamName } from "@/lib/teams";
import { PointsChart } from "@/components/charts/PointsChart";
import { Card, Eyebrow, Headline, ResultChip, Skeleton, StatTile, TeamSwatch } from "@/components/ui";

// Which seasons the toggle offers. The API has every season back to 1999;
// these two are the ones the model was tested on.
const SEASONS = [2025, 2026];

export default function TeamPage({ params, searchParams }: PageProps<"/teams/[abbr]">) {
  return (
    <Suspense fallback={<TeamSkeleton />}>
      <TeamContent params={params} searchParams={searchParams} />
    </Suspense>
  );
}

async function TeamContent({ params, searchParams }: PageProps<"/teams/[abbr]">) {
  const { abbr } = await params;
  // Whole numbers only; anything else falls back to the team's latest season
  const rawSeason = Number((await searchParams).season);
  const season = Number.isInteger(rawSeason) && rawSeason > 0 ? rawSeason : undefined;
  const team = await getTeam(abbr, season);
  if (!team) notFound();

  const s = team.season_stats;
  const [city, nickname] = splitTeamName(team.name);
  const form = team.recent_form;

  return (
    <div className="flex flex-col gap-10 pt-10 sm:pt-16">
      <section className="flex flex-col gap-6">
        <Link href="/teams" className="text-sm text-fg-3 hover:text-fg">
          ← All teams
        </Link>
        <div className="flex items-center gap-3">
          <TeamSwatch abbr={team.abbr} size="lg" />
          <Eyebrow>
            {team.abbr} · {team.division}
          </Eyebrow>
        </div>
        <Headline before={city} accent={nickname} />
        <nav aria-label="Season" className="flex gap-2">
          {SEASONS.map((y) => (
            <Link
              key={y}
              href={`/teams/${team.abbr}?season=${y}`}
              scroll={false}
              aria-current={y === s.season ? "page" : undefined}
              className={`rounded-full px-3.5 py-1.5 text-sm ${
                y === s.season ? "bg-accent font-semibold text-accent-ink" : "bg-card text-fg-2 ring-1 ring-line hover:text-fg"
              }`}
            >
              {y}
            </Link>
          ))}
        </nav>
      </section>

      <section aria-label="Season stats" className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatTile label="Record" value={record(s.wins, s.losses, s.ties)} note={`${s.games} games played`} highlight />
        <StatTile delay={70} label="Points per game" value={s.avg_points_for.toFixed(1)} note={`${s.points_for} total`} />
        <StatTile delay={140} label="Allowed per game" value={s.avg_points_against.toFixed(1)} note={`${s.points_against} total`} />
        <StatTile delay={210}
          label="Point diff"
          value={signed(s.point_diff)}
          note={`Home ${record(s.home_wins, s.home_losses)} · Away ${record(s.away_wins, s.away_losses)}`}
        />
      </section>

      <Card className="p-5 sm:p-8">
        <div className="mb-6 flex flex-col gap-1">
          <Eyebrow>{s.season} regular season</Eyebrow>
          <h2 className="font-serif text-3xl text-fg sm:text-4xl">
            Points <em className="text-accent">per game</em>
          </h2>
        </div>
        <PointsChart games={team.season_games} />
        <details className="mt-6 text-sm">
          <summary className="cursor-pointer text-fg-3 hover:text-fg">Show as a table</summary>
          <div className="mt-4 overflow-x-auto">
            <table className="w-full min-w-[28rem] text-left tabular-nums">
              <thead className="text-xs uppercase tracking-[0.14em] text-fg-3">
                <tr>
                  <th className="py-2 font-medium">Week</th>
                  <th className="py-2 font-medium">Opponent</th>
                  <th className="py-2 font-medium">Result</th>
                  <th className="py-2 text-right font-medium">Scored</th>
                  <th className="py-2 text-right font-medium">Allowed</th>
                </tr>
              </thead>
              <tbody className="text-fg-2">
                {team.season_games.map((g) => (
                  <tr key={g.week} className="border-t border-line">
                    <td className="py-2">{g.week}</td>
                    <td className="py-2">
                      {g.home_away === "home" ? "vs" : "at"} {g.opponent}
                    </td>
                    <td className="py-2">{g.result}</td>
                    <td className="py-2 text-right text-fg">{g.points_for}</td>
                    <td className="py-2 text-right">{g.points_against}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </details>
      </Card>

      <Card className="p-5 sm:p-8">
        <div className="mb-6 flex flex-wrap items-end justify-between gap-2">
          <div className="flex flex-col gap-1">
            <Eyebrow>Last {form.games.length} games</Eyebrow>
            <h2 className="font-serif text-3xl text-fg sm:text-4xl">
              Recent <em className="text-accent">form</em>
            </h2>
          </div>
          <p className="text-sm text-fg-2">
            {record(form.wins, form.losses, form.ties)} · avg margin {signed(form.avg_point_diff)}
          </p>
        </div>
        <ul className="flex flex-col divide-y divide-line">
          {form.games.map((g) => (
            <li key={g.game_id} className="flex items-center gap-4 py-3">
              <ResultChip result={g.result} />
              <TeamSwatch abbr={g.opponent} size="sm" />
              <Link href={`/teams/${g.opponent}`} className="text-fg hover:text-accent">
                {g.home_away === "home" ? "vs" : "at"} {g.opponent}
              </Link>
              <span className="hidden text-sm text-fg-3 sm:inline">
                {g.season} · Wk {g.week} · {gameDate(g.gameday)}
              </span>
              <span className="ml-auto tabular-nums text-fg-2">
                {g.points_for}–{g.points_against}
              </span>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}

function TeamSkeleton() {
  return (
    <div className="flex flex-col gap-10 pt-10 sm:pt-16">
      <Skeleton className="h-40" />
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[0, 1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-36" />
        ))}
      </div>
      <Skeleton className="h-96" />
    </div>
  );
}
