import { Suspense } from "react";
import type { Metadata } from "next";
import { getAccuracy } from "@/lib/api";
import { pct } from "@/lib/format";
import { AccuracyChart } from "@/components/charts/AccuracyChart";
import { Card, Eyebrow, Headline, Skeleton, StatTile } from "@/components/ui";

export const metadata: Metadata = { title: "Model" };

const METHODS = ["Logistic regression", "Vegas favorite", "Always pick home team"];

export default function ModelPage() {
  return (
    <div className="flex flex-col gap-12 pt-10 sm:pt-20">
      <section>
        <Headline before="Is the model any" accent="good" after="?" />
        <p className="mt-6 max-w-xl text-lg leading-relaxed text-fg-2">
          Every season is predicted by a model that never saw it: trained on the years before, then
          scored against two simple baselines.
        </p>
      </section>
      <Suspense fallback={<Skeleton className="h-[36rem]" />}>
        <ModelContent />
      </Suspense>
    </div>
  );
}

async function ModelContent() {
  const seasons = await getAccuracy();
  // The headline numbers use the last COMPLETE season; a season in progress
  // is too small a sample to lead with.
  const complete = [...seasons].reverse().find((s) => s.games_remaining === 0) ?? seasons[0];
  const get = (name: string) => complete?.methods.find((m) => m.method === name);
  const model = get("Logistic regression");
  const vegas = get("Vegas favorite");
  const home = get("Always pick home team");
  const inProgress = seasons.find((s) => s.games_remaining > 0);

  return (
    <div className="flex flex-col gap-10">
      {complete && model && vegas && home && (
        <section aria-label={`${complete.season} results`} className="grid grid-cols-3 gap-2 sm:gap-4">
          <StatTile label={`Model · ${complete.season}`} value={pct(model.accuracy)} note={`${model.correct} of ${complete.games} games`} highlight />
          <StatTile label="Vegas favorite" value={pct(vegas.accuracy)} note={`${vegas.correct} of ${complete.games}`} />
          <StatTile label="Always pick home" value={pct(home.accuracy)} note={`${home.correct} of ${complete.games}`} />
        </section>
      )}

      <Card className="p-5 sm:p-8">
        <div className="mb-6 flex flex-col gap-1">
          <Eyebrow>Share of games picked correctly · ties excluded</Eyebrow>
          <h2 className="font-serif text-3xl text-fg sm:text-4xl">
            Model <em className="text-accent">vs</em> baselines
          </h2>
        </div>
        <AccuracyChart seasons={seasons} />
        <details className="mt-6 text-sm">
          <summary className="cursor-pointer text-fg-3 hover:text-fg">Show as a table</summary>
          <div className="mt-4 overflow-x-auto">
            <table className="w-full min-w-[32rem] text-left tabular-nums">
              <thead className="text-xs uppercase tracking-[0.14em] text-fg-3">
                <tr>
                  <th className="py-2 font-medium">Season</th>
                  <th className="py-2 font-medium">Trained on</th>
                  {METHODS.map((m) => (
                    <th key={m} className="py-2 text-right font-medium">
                      {m}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="text-fg-2">
                {seasons.map((s) => (
                  <tr key={s.season} className="border-t border-line">
                    <td className="py-2 text-fg">
                      {s.season}
                      {s.games_remaining > 0 && <span className="text-fg-3"> (so far)</span>}
                    </td>
                    <td className="py-2">{s.trained_on}</td>
                    {METHODS.map((name) => {
                      const m = s.methods.find((x) => x.method === name);
                      return (
                        <td key={name} className="py-2 text-right">
                          {m ? `${m.correct}/${s.games} · ${pct(m.accuracy)}` : "–"}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </details>
      </Card>

      <section className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Note title="Never sees the future">
          The 2025 model trained on 2018 to 2024; the 2026 model on 2018 to 2025. Features only use
          games played before kickoff.
        </Note>
        <Note title="Why Vegas still wins">
          Betting lines include injuries, quarterback news and market money. This model sees recent
          scoring, win percentage, rest and divisional games.
        </Note>
        <Note title="Small samples swing">
          {inProgress
            ? `${inProgress.season} has ${inProgress.games} games scored and ${inProgress.games_remaining} still to play, so its numbers will move.`
            : "One season is about 270 games, so a few lucky weeks move the numbers by several points."}
        </Note>
      </section>
    </div>
  );
}

function Note({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <Card className="p-6">
      <h3 className="font-serif text-2xl text-fg">{title}</h3>
      <p className="mt-3 text-sm leading-relaxed text-fg-2">{children}</p>
    </Card>
  );
}
