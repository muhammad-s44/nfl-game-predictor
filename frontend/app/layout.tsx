import type { Metadata } from "next";
import { Instrument_Serif, Inter } from "next/font/google";
import Link from "next/link";
import "./globals.css";

// next/font downloads the fonts at build time and serves them from this
// site, so pages don't wait on Google Fonts.
const serif = Instrument_Serif({
  variable: "--font-instrument-serif",
  weight: "400",
  style: ["normal", "italic"],
  subsets: ["latin"],
});

const sans = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: { default: "Game Predictor", template: "%s · Game Predictor" },
  description: "Win probabilities for every game, from a logistic regression trained on past seasons.",
};

const NAV = [
  { href: "/", label: "This week" },
  { href: "/teams", label: "Teams" },
  { href: "/model", label: "Model" },
];

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${serif.variable} ${sans.variable} h-full antialiased`}>
      <body className="flex min-h-full flex-col">
        <header className="mx-auto flex w-full max-w-6xl items-center justify-between gap-4 px-4 py-6 sm:px-8">
          <Link href="/" className="whitespace-nowrap font-serif text-xl tracking-tight text-fg sm:text-2xl">
            Game <em className="text-accent">Predictor</em>
          </Link>
          <nav className="flex gap-0.5 text-sm sm:gap-1">
            {NAV.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="whitespace-nowrap rounded-full px-2 py-1.5 text-fg-2 transition-colors hover:bg-card hover:text-fg sm:px-3"
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </header>

        <main className="mx-auto w-full max-w-6xl flex-1 px-4 pb-24 sm:px-8">{children}</main>

        <footer className="mx-auto w-full max-w-6xl px-4 py-10 text-xs leading-relaxed text-fg-3 sm:px-8">
          Predictions from a logistic regression trained on nflverse game data. Team abbreviations
          and colours only; no logos. Not betting advice.
        </footer>
      </body>
    </html>
  );
}
