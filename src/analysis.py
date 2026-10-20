import re
import sqlite3
from pathlib import Path

import pandas as pd
from scipy.stats import chi2_contingency, mannwhitneyu

BASE = Path(__file__).resolve().parents[1]
DB = BASE / "data" / "processed" / "food_hygiene.db"
SQL_FILE = BASE / "sql" / "analysis.sql"
RESULTS = BASE / "results"

RESULTS.mkdir(exist_ok=True)


def fmt_p(p):
    return "p < 0.0001" if p < 0.0001 else f"p = {p:.3f}"

sql_text = SQL_FILE.read_text()
queries = dict(re.findall(r"-- name: (\w+)\n(.*?);", sql_text, flags=re.S))

with sqlite3.connect(DB) as conn:
    for name, query in queries.items():
        result = pd.read_sql_query(query, conn)
        result.to_csv(RESULTS / f"{name}.csv", index=False)
        print(f"\n=== {name} ===")
        print(result.to_string(index=False))

    df = pd.read_sql_query("SELECT * FROM establishments", conn)

rated = df.dropna(subset=["rating"])
cardiff = rated[rated["city"] == "Cardiff"]
london = rated[rated["city"] == "London"]

print("\n=== Statistical tests ===")

u, p = mannwhitneyu(cardiff["rating"], london["rating"])
print(f"Rating distributions (Mann-Whitney U): {fmt_p(p)}")

five = pd.crosstab(rated["city"], rated["rating"] == 5)
chi2, p, _, _ = chi2_contingency(five)
print(f"Share rated 5 (chi-square): {fmt_p(p)}")

awaiting = pd.crosstab(df["city"], df["rating_status"] == "Awaiting inspection")
chi2, p, _, _ = chi2_contingency(awaiting)
print(f"Share awaiting inspection (chi-square): {fmt_p(p)}")

scores = ["hygiene_score", "structural_score", "management_score"]
corr = rated[["rating"] + scores].corr(method="spearman")["rating"][scores]
print("\nSpearman correlation with rating:")
print(corr.round(2).to_string())

print("\nA p-value below 0.05 suggests the difference is unlikely to be chance.")