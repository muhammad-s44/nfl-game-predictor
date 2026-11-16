/** Legend shown above every multi-series chart: colour swatch + text-coloured label. */
export function ChartLegend({ items }: { items: { label: string; color: string }[] }) {
  return (
    <ul className="flex flex-wrap gap-x-5 gap-y-2 text-sm text-fg-2">
      {items.map((item) => (
        <li key={item.label} className="flex items-center gap-2">
          <span aria-hidden className="h-2.5 w-2.5 rounded-full" style={{ background: item.color }} />
          {item.label}
        </li>
      ))}
    </ul>
  );
}

/** Tooltip box shared by both charts. */
export function TooltipBox({ title, rows }: { title: string; rows: { label: string; value: string; color: string }[] }) {
  return (
    <div className="min-w-44 rounded-2xl bg-card-2 px-4 py-3 text-sm shadow-float ring-1 ring-line">
      <p className="mb-2 text-xs uppercase tracking-[0.14em] text-fg-3">{title}</p>
      {rows.map((r) => (
        <p key={r.label} className="flex items-center justify-between gap-6 text-fg-2">
          <span className="flex items-center gap-2">
            <span aria-hidden className="h-2 w-2 rounded-full" style={{ background: r.color }} />
            {r.label}
          </span>
          <span className="tabular-nums text-fg">{r.value}</span>
        </p>
      ))}
    </div>
  );
}

// Chart colours, read from the same values as the CSS tokens in globals.css.
// (Recharts draws SVG and takes colour strings, not Tailwind classes.)
export const VIZ = {
  model: "#7fa516",
  vegas: "#5f86cc",
  home: "#d0688a",
  surface: "#171916",
  grid: "rgba(237,233,223,0.08)",
  axis: "#8a857a",
  label: "#b5b0a4",
};
