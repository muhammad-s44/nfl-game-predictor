import type { ReactNode } from "react";
import { teamColors } from "@/lib/teams";

/** A floating card: the basic surface every block of data sits on. */
export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <div className={`rounded-3xl bg-card shadow-float ring-1 ring-line ${className}`}>{children}</div>
  );
}

/** Small uppercase label above headlines and inside cards. */
export function Eyebrow({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <p className={`text-xs font-medium uppercase tracking-[0.18em] text-fg-3 ${className}`}>
      {children}
    </p>
  );
}

/**
 * The big serif page headline. Pass the accent word as `accent`; it renders
 * in italic and in the bright accent colour.
 */
export function Headline({
  before,
  accent,
  after = "",
}: {
  before: string;
  accent: string;
  after?: string;
}) {
  return (
    <h1 className="font-serif text-[clamp(2.75rem,9vw,6.5rem)] leading-[0.95] tracking-tight text-fg text-balance">
      {before} <em className="text-accent">{accent}</em>
      {after}
    </h1>
  );
}

/** One headline number with a label: used in hero rows and stat grids. */
export function StatTile({
  label,
  value,
  note,
  highlight = false,
}: {
  label: string;
  value: string;
  note?: string;
  highlight?: boolean;
}) {
  return (
    <Card className="p-4 sm:p-6">
      <p className="text-[10px] font-medium uppercase tracking-[0.12em] text-fg-3 sm:text-xs sm:tracking-[0.18em]">
        {label}
      </p>
      <p className={`mt-3 font-serif text-3xl leading-none sm:text-5xl ${highlight ? "text-accent" : "text-fg"}`}>
        {value}
      </p>
      {note && <p className="mt-2 text-xs text-fg-3 sm:text-sm">{note}</p>}
    </Card>
  );
}

/** Two-tone team colour chip. Decorative: the abbreviation next to it carries the name. */
export function TeamSwatch({ abbr, size = "md" }: { abbr: string; size?: "sm" | "md" | "lg" }) {
  const [primary, secondary] = teamColors(abbr);
  const dims = { sm: "h-3 w-3", md: "h-4 w-4", lg: "h-6 w-6" }[size];
  return (
    <span
      aria-hidden
      className={`${dims} inline-block shrink-0 rounded-full ring-1 ring-fg/20`}
      style={{ background: `linear-gradient(135deg, ${primary} 50%, ${secondary} 50%)` }}
    />
  );
}

/** W / L / T chip. Shape and letter carry the meaning, not colour alone. */
export function ResultChip({ result }: { result: "W" | "L" | "T" }) {
  const style =
    result === "W"
      ? "bg-accent text-accent-ink"
      : result === "L"
        ? "bg-card-2 text-fg-2 ring-1 ring-line"
        : "bg-card-2 text-fg-3 ring-1 ring-line";
  return (
    <span className={`inline-flex h-7 w-7 items-center justify-center rounded-full text-xs font-semibold ${style}`}>
      {result}
    </span>
  );
}

/** Placeholder block shown while data streams in. */
export function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded-3xl bg-card/60 ring-1 ring-line ${className}`} />;
}
