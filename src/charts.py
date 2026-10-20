import sqlite3
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parents[1]
DB = BASE / "data" / "processed" / "food_hygiene.db"
CHARTS = BASE / "charts"

CHARTS.mkdir(exist_ok=True)

with sqlite3.connect(DB) as conn:
    df = pd.read_sql_query("SELECT * FROM establishments", conn)

rated = df.dropna(subset=["rating"])

cardiff_colour = "#8C6BB1"
westminster_colour = "#C4A4D8"
colours = [cardiff_colour, westminster_colour]

averages = rated.groupby("location")["rating"].mean()
averages = averages.reindex(["Cardiff", "Westminster"])

fig, ax = plt.subplots(figsize=(8, 5))

bars = ax.bar(averages.index, averages.values, color=colours, width=0.55)

ax.set_title("Average food hygiene rating", fontsize=16, pad=18)
ax.set_ylabel("Average rating (out of 5)")
ax.set_ylim(0, 5.3)

for bar, value in zip(bars, averages.values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        value + 0.06,
        f"{value:.2f}",
        ha="center",
        fontsize=12,
        fontweight="bold"
    )

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.savefig(CHARTS / "average_rating.png", dpi=200)
plt.close()

five_star = rated.groupby("location")["rating"].apply(
    lambda ratings: (ratings == 5).mean() * 100
)

five_star = five_star.reindex(["Cardiff", "Westminster"])

fig, ax = plt.subplots(figsize=(8, 5))

bars = ax.bar(
    five_star.index,
    five_star.values,
    color=colours,
    width=0.55
)

ax.set_title("Businesses rated 5", fontsize=16, pad=18)
ax.set_ylabel("Percentage of rated businesses")
ax.set_ylim(0, 100)

for bar, value in zip(bars, five_star.values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        value + 1.5,
        f"{value:.2f}%",
        ha="center",
        fontsize=12,
        fontweight="bold"
    )

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.savefig(CHARTS / "five_star.png", dpi=200)
plt.close()

types = rated.groupby(
    ["business_type", "location"]
)["rating"].agg(["mean", "count"]).reset_index()

types = types[types["count"] >= 10]

comparison = types.pivot(
    index="business_type",
    columns="location",
    values="mean"
)

comparison = comparison.reindex(columns=["Cardiff", "Westminster"])

comparison = comparison.dropna()

comparison = comparison.sort_values("Cardiff")

fig, ax = plt.subplots(figsize=(12, 8))

comparison.plot.barh(
    ax=ax,
    color=colours,
    width=0.75
)

ax.set_title("Average rating by business type", fontsize=16, pad=18)
ax.set_xlabel("Average rating (out of 5)")
ax.set_ylabel("")
ax.set_xlim(0, 5.2)

ax.legend(
    title="",
    loc="upper center",
    bbox_to_anchor=(0.5, -0.09),
    ncol=2,
    frameon=False
)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.grid(axis="x", alpha=0.15)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(
    CHARTS / "business_types.png",
    dpi=200,
    bbox_inches="tight"
)
plt.close()

print("All three charts updated.")
