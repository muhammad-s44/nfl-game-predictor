"use client";

import { useEffect, useState } from "react";
import { useInView, useReducedMotion } from "@/lib/useInView";

const NUMBER = /\d+(?:\.\d+)?/g;
const DURATION_MS = 900;

/** Fast at the start, gentle at the end. */
const easeOutCubic = (t: number) => 1 - (1 - t) ** 3;

/**
 * Counts every number inside `text` up from 0 once it scrolls into view,
 * keeping everything else ("%", "–", "+", decimals) exactly as written:
 * "52.2%" counts 0.0% -> 52.2%, "6–11" counts both sides.
 *
 * The server renders the final text, so search engines, no-JS visitors and
 * reduced-motion users always see the real value. Before the number scrolls
 * into view it sits at 0, while its card is still faded out.
 */
export function CountUp({ text }: { text: string }) {
  const [ref, inView] = useInView<HTMLSpanElement>();
  const reduced = useReducedMotion();
  const [progress, setProgress] = useState(0); // 0 -> 1 over the animation

  useEffect(() => {
    if (!inView || reduced) return;
    let frame = 0;
    const start = performance.now();
    // State only changes inside animation-frame callbacks, once per frame
    const tick = (now: number) => {
      const t = Math.min((now - start) / DURATION_MS, 1);
      setProgress(easeOutCubic(t));
      if (t < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [inView, reduced]);

  const shown =
    reduced || progress >= 1
      ? text
      : text.replace(NUMBER, (match) => {
          const decimals = match.split(".")[1]?.length ?? 0;
          return (Number(match) * progress).toFixed(decimals);
        });

  // tabular-nums keeps digits the same width, so the text doesn't wobble
  return (
    <span ref={ref} className="tabular-nums">
      {shown}
    </span>
  );
}
