import Link from "next/link";
import { Card, Eyebrow } from "@/components/ui";

export default function NotFound() {
  return (
    <div className="pt-16">
      <Card className="mx-auto max-w-xl p-8">
        <Eyebrow>404</Eyebrow>
        <h1 className="mt-3 font-serif text-4xl text-fg">
          Nothing <em className="text-accent">here</em>.
        </h1>
        <p className="mt-4 text-fg-2">That team or week doesn&apos;t exist in the data.</p>
        <Link href="/" className="mt-6 inline-block rounded-full bg-accent px-5 py-2 text-sm font-semibold text-accent-ink">
          Back to this week
        </Link>
      </Card>
    </div>
  );
}
