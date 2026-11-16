import { Suspense } from "react";
import { notFound } from "next/navigation";
import { getAccuracy, getPredictions } from "@/lib/api";
import { pct } from "@/lib/format";
import { GameCard } from "@/components/GameCard";
import { WeekPicker } from "@/components/WeekPicker";
import { Eyebrow, Headline, Skeleton, StatTile } from "@/components/ui";

// The page itself is static: the headline is part of the prerendered shell
// and shows instantly. Everything that reads the URL (?week=) or calls the
// API sits inside <Suspense>, so it streams in at request time. With Cache
// Components on, Next.js requires that split.
export default function Home({ searchParams }: PageProps<"/">) {
  return (
    <div>
      <section className="pt-10 pb-12 sm:pt-20 sm:pb-16">
        <Headline before="Every game," accent="called" after=" before kickoff." />
        <p className="mt-6 max-w-xl text-lg leading-relaxed text-fg-2">
          A logistic regression trained only on past seasons picks every game. Here is the week, with
          the Vegas line beside each pick so you can see where they disagree.
        </p>
      </section>

      <Suspense fallback={<WeekSkeleton />}>
        <WeekContent searchParams={searchParams} />
      </Suspense>
    </div>
  );
}

async function WeekContent({ searchParams }: Pick<PageProps<"/">, "searchParams">) {
  const params = await searchParams;
  const week = Number(params.week) || undefined; // missing or junk -> current week
  const [predictions, accuracy] = await Promise.all([getPredictions(week), getAccuracy()]);
  if (!predictions) notFound();

  const thisSeason = accuracy.find((s) => s.season === predictions.season);
  const byMethod = (name: string) => thisSeason?.methods.find((m) => m.method === name);
  const model = byMethod("Logistic regression");
  const vegas = byMethod("Vegas favorite");
  const home = byMethod("Always pick home team");

  return (
    <div className="flex flex-col gap-10">
      {thisSeason && model && vegas && home && (
        <section aria-label="Season so far" className="grid grid-cols-3 gap-2 sm:gap-4">
          <StatTile
            label={`Model · ${predictions.season}`}
            value={pct(model.accuracy)}
            note={`${model.correct} of ${thisSeason.games} games right`}
            highlight
          />
          <StatTile label="Vegas favorite" value={pct(vegas.accuracy)} note={`${vegas.correct} of ${thisSeason.games}`} />
          <StatTile label="Always pick home" value={pct(home.accuracy)} note={`${home.correct} of ${thisSeason.games}`} />
        </section>
      )}

      <section className="flex flex-col gap-6">
        <div className="flex flex-col gap-4">
          <Eyebrow>
            {predictions.season} season · Week {predictions.week} · {predictions.games.length} games
          </Eyebrow>
          <WeekPicker weeks={predictions.weeks} current={predictions.week} />
        </div>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {predictions.games.map((g) => (
            <GameCard key={g.game_id} game={g} />
          ))}
        </div>
      </section>
    </div>
  );
}

function WeekSkeleton() {
  return (
    <div className="flex flex-col gap-10">
      <div className="grid grid-cols-3 gap-2 sm:gap-4">
        {[0, 1, 2].map((i) => (
          <Skeleton key={i} className="h-36" />
        ))}
      </div>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {[0, 1, 2, 3, 4, 5].map((i) => (
          <Skeleton key={i} className="h-64" />
        ))}
      </div>
    </div>
  );
}
