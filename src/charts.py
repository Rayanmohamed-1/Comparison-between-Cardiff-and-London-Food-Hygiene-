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

CITIES = ["Cardiff", "London"]

LABELS = {"Cardiff": "Cardiff", "London": "London\n(Westminster)"}
colours = ["#8C6BB1", "#C4A4D8"]


def style(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def bar_with_labels(ax, series, fmt, offset):
    bars = ax.bar(
        [LABELS[c] for c in series.index],
        series.values,
        color=colours,
        width=0.55,
    )
    for bar, value in zip(bars, series.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + offset,
            fmt.format(value),
            ha="center",
            fontsize=12,
            fontweight="bold",
        )


averages = rated.groupby("city")["rating"].mean().reindex(CITIES)

fig, ax = plt.subplots(figsize=(8, 5))
bar_with_labels(ax, averages, "{:.2f}", 0.06)
ax.set_title("Average food hygiene rating", fontsize=16, pad=18)
ax.set_ylabel("Average rating (out of 5)")
ax.set_ylim(0, 5.3)
style(ax)
plt.tight_layout()
plt.savefig(CHARTS / "average_rating.png", dpi=200)
plt.close()

five_star = (
    rated.groupby("city")["rating"].apply(lambda r: (r == 5).mean() * 100)
    .reindex(CITIES)
)

fig, ax = plt.subplots(figsize=(8, 5))
bar_with_labels(ax, five_star, "{:.2f}%", 1.5)
ax.set_title("Businesses rated 5", fontsize=16, pad=18)
ax.set_ylabel("Percentage of rated businesses")
ax.set_ylim(0, 100)
style(ax)
plt.tight_layout()
plt.savefig(CHARTS / "five_star.png", dpi=200)
plt.close()

status = (
    df.groupby("city")["rating_status"]
    .value_counts(normalize=True)
    .mul(100)
    .unstack(fill_value=0)
    .reindex(CITIES)
)
status = status[["Awaiting inspection", "Exempt"]]

fig, ax = plt.subplots(figsize=(8, 5))
status.plot.bar(ax=ax, color=["#8C6BB1", "#C4A4D8"], width=0.7, rot=0)
ax.set_xticklabels([LABELS[c] for c in status.index])
ax.set_title("Businesses without a rating", fontsize=16, pad=18)
ax.set_xlabel("")
ax.set_ylabel("Percentage of all businesses")
for container in ax.containers:
    ax.bar_label(container, fmt="%.1f%%", fontsize=11, fontweight="bold", padding=3)
ax.set_ylim(0, status.values.max() * 1.2)
ax.legend(title="", frameon=False)
style(ax)
plt.tight_layout()
plt.savefig(CHARTS / "unrated_share.png", dpi=200)
plt.close()

types = rated.groupby(["business_type", "city"])["rating"].agg(["mean", "count"])
types = types.reset_index()
types = types[types["count"] >= 10]

comparison = types.pivot(index="business_type", columns="city", values="mean")
comparison = comparison.reindex(columns=CITIES).dropna().sort_values("Cardiff")
comparison.columns = ["Cardiff", "London (Westminster)"]

fig, ax = plt.subplots(figsize=(12, 8))
comparison.plot.barh(ax=ax, color=colours, width=0.75)
ax.set_title("Average rating by business type", fontsize=16, pad=18)
ax.set_xlabel("Average rating (out of 5)")
ax.set_ylabel("")
ax.set_xlim(0, 5.2)
ax.legend(
    title="",
    loc="upper center",
    bbox_to_anchor=(0.5, -0.09),
    ncol=2,
    frameon=False,
)
ax.grid(axis="x", alpha=0.15)
ax.set_axisbelow(True)
style(ax)
plt.tight_layout()
plt.savefig(CHARTS / "business_types.png", dpi=200, bbox_inches="tight")
plt.close()

print("All four charts updated.")