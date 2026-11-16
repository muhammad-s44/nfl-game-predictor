"use client";

import { useEffect, useRef, useState, useSyncExternalStore } from "react";

/**
 * True once the element has scrolled into view (and stays true).
 * IntersectionObserver asks the browser to tell us when the element crosses
 * into the viewport, instead of checking on every scroll event.
 */
export function useInView<T extends Element>() {
  const ref = useRef<T>(null);
  const [inView, setInView] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el || inView) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setInView(true);
          observer.disconnect(); // animate once, not every time it re-enters
        }
      },
      // Trigger slightly before the bottom edge, once 15% of it is showing
      { rootMargin: "0px 0px -8% 0px", threshold: 0.15 },
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [inView]);

  return [ref, inView] as const;
}

const REDUCED = "(prefers-reduced-motion: reduce)";

/**
 * True when the user has asked their OS for less motion, and updates live if
 * they change it. useSyncExternalStore is React's way to read browser state:
 * during server rendering and hydration it uses the third argument (true =
 * "no animation", which matches the server HTML), then switches to the real
 * value on the client without a hydration mismatch.
 */
export function useReducedMotion() {
  return useSyncExternalStore(
    (onChange) => {
      const mq = window.matchMedia(REDUCED);
      mq.addEventListener("change", onChange);
      return () => mq.removeEventListener("change", onChange);
    },
    () => window.matchMedia(REDUCED).matches,
    () => true,
  );
}
