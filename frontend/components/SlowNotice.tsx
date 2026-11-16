"use client";

import { useEffect, useState } from "react";

/**
 * Shown inside loading skeletons. If data hasn't arrived after a few seconds,
 * explain why: the free API host sleeps when idle and needs time to wake.
 * Most loads finish before this ever appears.
 */
export function SlowNotice({ afterMs = 3000 }: { afterMs?: number }) {
  const [show, setShow] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setShow(true), afterMs);
    return () => clearTimeout(timer);
  }, [afterMs]);

  if (!show) return null;
  return (
    <p role="status" className="rounded-2xl bg-card px-4 py-3 text-sm text-fg-2 ring-1 ring-line">
      Waking up the prediction server. It runs on a free host that sleeps when nobody has
      visited for a while, so the first load can take up to a minute.
    </p>
  );
}
