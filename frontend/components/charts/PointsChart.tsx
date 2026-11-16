"use client";
// Recharts measures the screen and handles hover, so it runs in the browser:
// "use client" makes this a Client Component. The page around it stays a
// Server Component and passes the data in as props.

import {
  CartesianGrid,
  LabelList,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  type TooltipContentProps,
} from "recharts";
import type { SeasonGame } from "@/lib/types";
import { useInView } from "@/lib/useInView";
import { ChartLegend, TooltipBox, VIZ } from "./ChartLegend";

type Point = SeasonGame;

export function PointsChart({ games }: { games: SeasonGame[] }) {
  const [ref, inView] = useInView<HTMLDivElement>();
  const data: Point[] = games;
  const last = data.length - 1;

  // Direct label on the final point only: the series name, in text colour.
  // When the two final values are close, push the labels apart so they
  // don't overlap: the higher line's label goes up, the lower one's down.
  const end = data[last];
  const gap = end ? end.points_for - end.points_against : 0;
  const nudge = Math.abs(gap) < 5 ? 7 : 0;
  const scoredOnTop = gap >= 0;
  const endLabel = (name: string, isScored: boolean) =>
    function EndLabel(props: { index?: number; x?: number | string; y?: number | string }) {
      if (props.index !== last) return null;
      const dy = isScored === scoredOnTop ? -nudge : nudge;
      return (
        <text x={Number(props.x) + 10} y={Number(props.y) + 4 + dy} fill={VIZ.label} fontSize={12}>
          {name}
        </text>
      );
    };

  return (
    <div className="flex flex-col gap-4">
      <ChartLegend
        items={[
          { label: "Points scored", color: VIZ.model },
          { label: "Points allowed", color: VIZ.vegas },
        ]}
      />
      {/* Mount the chart only once it scrolls into view, so its draw-in
          animation plays where the reader can see it. The div keeps its height. */}
      <div ref={ref} className="h-72 w-full sm:h-80">
        {inView && (
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 12, right: 64, bottom: 4, left: -16 }}>
            <CartesianGrid vertical={false} stroke={VIZ.grid} />
            {/* A numeric week axis (not a list of labels), so a bye week
                shows up as a wider gap instead of being silently skipped. */}
            <XAxis
              dataKey="week"
              type="number"
              domain={[1, 18]}
              ticks={[1, 3, 5, 7, 9, 11, 13, 15, 17]}
              tickFormatter={(w: number) => `W${w}`}
              tick={{ fill: VIZ.axis, fontSize: 12 }}
              tickLine={false}
              axisLine={{ stroke: VIZ.grid }}
            />
            <YAxis
              domain={[0, "auto"]}
              allowDecimals={false}
              tick={{ fill: VIZ.axis, fontSize: 12 }}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip
              cursor={{ stroke: VIZ.axis, strokeDasharray: "3 3" }}
              content={(props: TooltipContentProps) => <PointsTooltip {...props} />}
            />
            {(
              [
                ["points_for", "Scored", VIZ.model],
                ["points_against", "Allowed", VIZ.vegas],
              ] as const
            ).map(([key, name, color]) => (
              <Line
                key={key}
                dataKey={key}
                name={name}
                type="linear"
                stroke={color}
                strokeWidth={2}
                dot={{ r: 4, fill: color, stroke: VIZ.surface, strokeWidth: 2 }}
                activeDot={{ r: 6, fill: color, stroke: VIZ.surface, strokeWidth: 2 }}
                isAnimationActive="auto"
                animationDuration={900}
                animationEasing="ease-out"
              >
                <LabelList dataKey={key} content={endLabel(name, key === "points_for")} />
              </Line>
            ))}
          </LineChart>
        </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}

function PointsTooltip({ active, payload }: TooltipContentProps) {
  if (!active || !payload?.length) return null;
  const g = payload[0].payload as Point;
  const where = g.home_away === "home" ? "vs" : "at";
  return (
    <TooltipBox
      title={`Week ${g.week} · ${where} ${g.opponent} · ${g.result}`}
      rows={[
        { label: "Scored", value: String(g.points_for), color: VIZ.model },
        { label: "Allowed", value: String(g.points_against), color: VIZ.vegas },
      ]}
    />
  );
}
