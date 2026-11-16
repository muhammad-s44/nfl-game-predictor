"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  LabelList,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  type TooltipContentProps,
} from "recharts";
import type { SeasonAccuracy } from "@/lib/types";
import { pct } from "@/lib/format";
import { ChartLegend, TooltipBox, VIZ } from "./ChartLegend";

// Fixed order and colour per method. The colour follows the method, so a
// season with different numbers never repaints it.
const SERIES = [
  { key: "Logistic regression", short: "Model", color: VIZ.model },
  { key: "Vegas favorite", short: "Vegas", color: VIZ.vegas },
  { key: "Always pick home team", short: "Home team", color: VIZ.home },
] as const;

type Row = { season: string; games: number } & Record<string, number | string>;

export function AccuracyChart({ seasons }: { seasons: SeasonAccuracy[] }) {
  const data: Row[] = seasons.map((s) => {
    const row: Row = {
      season: s.games_remaining ? `${s.season} (so far)` : String(s.season),
      games: s.games,
    };
    for (const m of s.methods) {
      row[m.method] = m.accuracy;
      row[`${m.method} correct`] = m.correct;
    }
    return row;
  });

  return (
    <div className="flex flex-col gap-4">
      <ChartLegend items={SERIES.map((s) => ({ label: s.short, color: s.color }))} />
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 24, right: 8, bottom: 4, left: -16 }} barGap={2} barCategoryGap="24%">
            <CartesianGrid vertical={false} stroke={VIZ.grid} />
            <XAxis dataKey="season" tick={{ fill: VIZ.axis, fontSize: 12 }} tickLine={false} axisLine={{ stroke: VIZ.grid }} />
            {/* Bars start at zero: a cut-off axis would exaggerate the gaps */}
            <YAxis
              domain={[0, 1]}
              ticks={[0, 0.25, 0.5, 0.75, 1]}
              tickFormatter={(v: number) => pct(v, 0)}
              tick={{ fill: VIZ.axis, fontSize: 12 }}
              tickLine={false}
              axisLine={false}
            />
            <ReferenceLine
              y={0.5}
              stroke={VIZ.axis}
              strokeDasharray="4 4"
              label={{ value: "Coin flip", position: "insideTopRight", fill: VIZ.axis, fontSize: 11 }}
            />
            <Tooltip
              cursor={{ fill: "rgba(237,233,223,0.04)" }}
              content={(props: TooltipContentProps) => <AccuracyTooltip {...props} />}
            />
            {SERIES.map((s) => (
              <Bar key={s.key} dataKey={s.key} name={s.short} fill={s.color} radius={[4, 4, 0, 0]} isAnimationActive={false}>
                <LabelList
                  dataKey={s.key}
                  position="top"
                  formatter={(v: unknown) => pct(Number(v), 0)}
                  fill={VIZ.label}
                  fontSize={12}
                />
              </Bar>
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function AccuracyTooltip({ active, payload }: TooltipContentProps) {
  if (!active || !payload?.length) return null;
  const row = payload[0].payload as Row;
  return (
    <TooltipBox
      title={`${row.season} · ${row.games} games`}
      rows={SERIES.map((s) => ({
        label: s.short,
        value: `${row[`${s.key} correct`]} · ${pct(Number(row[s.key]))}`,
        color: s.color,
      }))}
    />
  );
}
