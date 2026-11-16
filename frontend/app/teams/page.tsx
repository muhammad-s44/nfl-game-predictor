import { Suspense } from "react";
import Link from "next/link";
import type { Metadata } from "next";
import { getTeams } from "@/lib/api";
import { record } from "@/lib/format";
import type { TeamSummary } from "@/lib/types";
import { Card, Eyebrow, Headline, Skeleton, TeamSwatch } from "@/components/ui";

export const metadata: Metadata = { title: "Teams" };

export default function TeamsPage() {
  return (
    <div className="flex flex-col gap-12 pt-10 sm:pt-20">
      <Headline before="All" accent="thirty-two" after=" teams." />
      <Suspense fallback={<Skeleton className="h-[40rem]" />}>
        <TeamsGrid />
      </Suspense>
    </div>
  );
}

async function TeamsGrid() {
  const data = await getTeams();
  if (!data) return null;

  // Group into divisions, keeping the API's order (conference, division, name)
  const divisions = new Map<string, TeamSummary[]>();
  for (const t of data.teams) {
    divisions.set(t.division, [...(divisions.get(t.division) ?? []), t]);
  }

  return (
    <div className="flex flex-col gap-8">
      <Eyebrow>{data.season} regular-season records</Eyebrow>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {[...divisions].map(([division, teams]) => (
          <Card key={division} className="p-5">
            <Eyebrow className="mb-4">{division}</Eyebrow>
            <ul className="flex flex-col">
              {teams.map((t) => (
                <li key={t.abbr}>
                  <Link
                    href={`/teams/${t.abbr}`}
                    className="-mx-2 flex items-center gap-3 rounded-xl px-2 py-2.5 transition-colors hover:bg-card-2"
                  >
                    <TeamSwatch abbr={t.abbr} />
                    <span className="w-10 shrink-0 font-semibold text-fg">{t.abbr}</span>
                    <span className="min-w-0 truncate text-sm text-fg-3">{t.name}</span>
                    <span className="ml-auto shrink-0 whitespace-nowrap tabular-nums text-sm text-fg-2">
                      {record(t.wins, t.losses, t.ties)}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          </Card>
        ))}
      </div>
    </div>
  );
}
