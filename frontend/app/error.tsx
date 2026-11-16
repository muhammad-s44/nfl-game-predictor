"use client";
// Shown when a page throws, most often because the API isn't running.

import { Card, Eyebrow } from "@/components/ui";

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div className="pt-16">
      <Card className="mx-auto max-w-xl p-8">
        <Eyebrow>Something went wrong</Eyebrow>
        <h1 className="mt-3 font-serif text-4xl text-fg">
          No <em className="text-accent">data</em> right now.
        </h1>
        <p className="mt-4 text-fg-2">{error.message}</p>
        <p className="mt-4 text-sm text-fg-3">
          Start the API from the repo root with <code className="text-fg-2">uvicorn backend.app.main:app</code>,
          then try again.
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
