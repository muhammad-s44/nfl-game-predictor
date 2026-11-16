"use client";

import type { ReactNode } from "react";
import { useInView } from "@/lib/useInView";

/**
 * Fades and slides its content in the first time it scrolls into view.
 * This component only toggles a class; the motion itself is CSS (.reveal in
 * globals.css), which also switches it off for reduced-motion users and when
 * JavaScript is unavailable, so content is never stuck invisible.
 */
export function Reveal({
  children,
  className = "",
  delay = 0,
}: {
  children: ReactNode;
  className?: string;
  delay?: number; // ms, for a small stagger between neighbouring cards
}) {
  const [ref, inView] = useInView<HTMLDivElement>();
  return (
    <div
      ref={ref}
      className={`reveal ${inView ? "is-visible" : ""} ${className}`}
      style={delay ? { transitionDelay: `${delay}ms` } : undefined}
    >
      {children}
    </div>
  );
}
