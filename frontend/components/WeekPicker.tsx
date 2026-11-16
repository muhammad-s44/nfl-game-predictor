import Link from "next/link";

/** A row of week pills. Plain links (?week=N), so it works without JavaScript. */
export function WeekPicker({ weeks, current }: { weeks: number[]; current: number }) {
  return (
    <nav aria-label="Choose a week" className="no-scrollbar -mx-4 flex gap-2 overflow-x-auto px-4 pb-1 sm:mx-0 sm:flex-wrap sm:px-0">
      {weeks.map((w) => {
        const active = w === current;
        return (
          <Link
            key={w}
            href={`/?week=${w}`}
            scroll={false}
            aria-current={active ? "page" : undefined}
            className={`shrink-0 rounded-full px-3.5 py-1.5 text-sm tabular-nums transition-colors ${
              active
                ? "bg-accent font-semibold text-accent-ink"
                : "bg-card text-fg-2 ring-1 ring-line hover:text-fg"
            }`}
          >
            Wk {w}
          </Link>
        );
      })}
    </nav>
  );
}
