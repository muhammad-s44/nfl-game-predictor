"use client";
// Shown when a page throws, most often because the API isn't running.
//
// In production, Next.js does NOT pass a server error's message to the
// browser (it could leak internals); the browser only gets a `digest` id
// that matches the full error in the server logs. So the friendly text here
// is fixed, and the real message is shown only in development.

import { Card, Eyebrow } from "@/components/ui";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const dev = process.env.NODE_ENV === "development";
  return (
    <div className="pt-16">
      <Card className="mx-auto max-w-xl p-8">
        <Eyebrow>Something went wrong</Eyebrow>
        <h1 className="mt-3 font-serif text-4xl text-fg">
          No <em className="text-accent">data</em> right now.
        </h1>
        <p className="mt-4 text-fg-2">
          The site couldn&apos;t load data from the prediction API. It may be down or still starting.
        </p>
        {dev && <p className="mt-3 font-mono text-xs text-fg-3">{error.message}</p>}
        {!dev && error.digest && <p className="mt-3 text-xs text-fg-3">Reference: {error.digest}</p>}
        <p className="mt-4 text-sm text-fg-3">
          Running it locally? Start the API from the repo root with{" "}
          <code className="text-fg-2">uvicorn backend.app.main:app</code>, then try again.
        </p>
        <button
          onClick={reset}
          className="mt-6 rounded-full bg-accent px-5 py-2 text-sm font-semibold text-accent-ink"
        >
          Try again
        </button>
      </Card>
    </div>
  );
}
