"""Stage 3a: save charts about the games data to charts/.

Run from the repo root (inside the virtual environment):
    python src/charts.py
"""

import os

import matplotlib

matplotlib.use("Agg")  # draw straight to files; no window needed
import matplotlib.pyplot as plt
import pandas as pd

from analysis import (
    DATA_PATH,
    add_underdog_columns,
    home_win_pct_by_season,
    load_games_df,
    underdog_win_rates,
)

CHART_DIR = "charts"

# One main color plus one highlight, so color always means the same thing
BLUE = "#2a78d6"
ORANGE = "#eb6834"
INK = "#0b0b0b"
MUTED = "#52514e"
GRID = "#e4e3df"
SURFACE = "#fcfcfb"


def style_axes(ax, title, xlabel, ylabel):
    """Apply the shared look: title, labels, light grid, no top/right border."""
    ax.set_title(title, loc="left", fontsize=13, color=INK, pad=12)
    ax.set_xlabel(xlabel, color=MUTED)
    ax.set_ylabel(ylabel, color=MUTED)
    ax.tick_params(colors=MUTED)
    ax.grid(color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)  # grid behind the data, not on top of it
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)


def save(fig, filename):
    """Save a figure into charts/ and close it to free memory."""
    path = os.path.join(CHART_DIR, filename)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)
    print(f"saved {path}")


def last_full_season(df):
    """Most recent season that has a Super Bowl, i.e. is complete."""
    return df.loc[df["game_type"] == "SB", "season"].max()


def chart_home_win_pct(df):
    """Line chart: home win % per season, with 2020 (no fans) called out."""
    by_season = home_win_pct_by_season(df[df["season"] <= last_full_season(df)])
    fig, ax = plt.subplots(figsize=(9, 4.5), facecolor=SURFACE)
    ax.plot(by_season.index, by_season.values * 100, color=BLUE, linewidth=2,
            marker="o", markersize=4)
    ax.axhline(50, color=MUTED, linestyle="--", linewidth=1)
    ax.text(by_season.index.min(), 50.4, "50% = no home advantage", color=MUTED,
            fontsize=9)
    ax.annotate("2020: empty stadiums", xy=(2020, by_season[2020] * 100),
                xytext=(2010.5, 51.2), color=INK, fontsize=9,
                arrowprops={"arrowstyle": "->", "color": MUTED})
    ax.set_ylim(48, 64)
    style_axes(ax, "Home teams win less often than they used to",
               "Season", "Home win % (decided, non-neutral games)")
    save(fig, "home_win_pct.png")


def chart_scoring_trend(df):
    """Line chart: average combined points per game, by season."""
    df = df[df["season"] <= last_full_season(df)]
    avg = (df["home_score"] + df["away_score"]).groupby(df["season"]).mean()
    fig, ax = plt.subplots(figsize=(9, 4.5), facecolor=SURFACE)
    ax.plot(avg.index, avg.values, color=BLUE, linewidth=2, marker="o", markersize=4)
    peak = avg.idxmax()
    ax.annotate(f"{peak}: {avg[peak]:.1f}", xy=(peak, avg[peak]),
                xytext=(peak - 7, avg[peak] - 0.3), color=INK, fontsize=9,
                arrowprops={"arrowstyle": "->", "color": MUTED})
    style_axes(ax, "Average points per game by season",
               "Season", "Combined points per game")
    save(fig, "scoring_trend.png")


def chart_underdog_wins(df):
    """Horizontal bars: each team's win % as the underdog, league average marked."""
    rates = underdog_win_rates(df).sort_values("win_pct")
    league = add_underdog_columns(df)["underdog_won"].mean()
    fig, ax = plt.subplots(figsize=(8, 10), facecolor=SURFACE)
    # Highlight the extremes so the eye goes straight to the story
    colors = [ORANGE if i >= len(rates) - 3 else BLUE for i in range(len(rates))]
    ax.barh(rates.index, rates["win_pct"] * 100, color=colors, height=0.7)
    ax.axvline(league * 100, color=INK, linestyle="--", linewidth=1)
    ax.text(league * 100 + 0.4, -1.3, f"League average {league:.1%}",
            color=INK, fontsize=9)
    ax.set_ylim(-1.8, len(rates) - 0.4)
    style_axes(ax, "Win % as the underdog, 1999-present",
               "Underdog win %", "")
    ax.grid(axis="y", visible=False)
    save(fig, "underdog_wins.png")


def favorite_win_pct_by_spread(df):
    """Group games by how big the spread was; return favorite win % per group."""
    df = add_underdog_columns(df)
    df = df[df["result"] != 0]  # ties have no winner
    size = df["spread_line"].abs()
    bins = [0, 3, 6, 9, 13, 30]
    labels = ["0.5-3", "3.5-6", "6.5-9", "9.5-13", "13.5+"]
    bucket = pd.cut(size, bins=bins, labels=labels)
    favorite_won = ~df["underdog_won"]
    grouped = favorite_won.groupby(bucket, observed=True)
    return pd.DataFrame({"win_pct": grouped.mean(), "games": grouped.size()})


def chart_favorite_by_spread(df):
    """Bar chart: how often the Vegas favorite wins, by size of the spread."""
    table = favorite_win_pct_by_spread(df)
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor=SURFACE)
    bars = ax.bar(table.index.astype(str), table["win_pct"] * 100, color=BLUE,
                  width=0.6)
    for bar, (pct, n) in zip(bars, zip(table["win_pct"], table["games"])):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f"{pct:.0%}\n{n} games", ha="center", color=INK, fontsize=9)
    ax.set_ylim(0, 105)
    style_axes(ax, "Bigger spreads, safer favorites",
               "Point spread (favorite's expected margin)", "Favorite win %")
    ax.grid(axis="x", visible=False)
    save(fig, "favorite_by_spread.png")


def main():
    os.makedirs(CHART_DIR, exist_ok=True)
    df = load_games_df(DATA_PATH)
    chart_home_win_pct(df)
    chart_scoring_trend(df)
    chart_underdog_wins(df)
    chart_favorite_by_spread(df)


if __name__ == "__main__":
    main()
