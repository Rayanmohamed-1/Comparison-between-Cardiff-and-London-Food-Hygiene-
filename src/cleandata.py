from pathlib import Path
import sqlite3
import xml.etree.ElementTree as ET

import pandas as pd

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"

SOURCES = {
    "cardiff.xml": ("Cardiff", "Cardiff"),
    "westminster.xml": ("London", "Westminster"),
}

DOWNLOAD_DATE = pd.Timestamp("2026-10-20")

STATUS_LABELS = {
    "AwaitingInspection": "Awaiting inspection",
    "Exempt": "Exempt",
    "AwaitingPublication": "Awaiting publication",
}

PROCESSED.mkdir(parents=True, exist_ok=True)


def read_fsa_xml(filename, city, borough):
    root = ET.parse(RAW / filename).getroot()
    records = []

    for business in root.findall(".//EstablishmentDetail"):
        scores = business.find("Scores")

        def score(field):
            return scores.findtext(field) if scores is not None else None

        records.append({
            "business_id": business.findtext("FHRSID"),
            "business_name": business.findtext("BusinessName"),
            "business_type": business.findtext("BusinessType"),
            "rating_raw": business.findtext("RatingValue"),
            "rating_date": business.findtext("RatingDate"),
            "hygiene_score": score("Hygiene"),
            "structural_score": score("Structural"),
            "management_score": score("ConfidenceInManagement"),
            "postcode": business.findtext("PostCode"),
            "city": city,
            "borough": borough,
        })

    df = pd.DataFrame(records)
    if df.empty:
        raise ValueError(f"No establishments found in {filename}")
    return df


def tidy(df):
    df["rating"] = pd.to_numeric(df["rating_raw"], errors="coerce")
    df["rating_status"] = df["rating_raw"].map(STATUS_LABELS)
    df.loc[df["rating"].notna(), "rating_status"] = "Rated"
    df["rating_status"] = df["rating_status"].fillna("Other")

    for column in ["hygiene_score", "structural_score", "management_score"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    inspected = pd.to_datetime(df["rating_date"], errors="coerce")
    df["days_since_inspection"] = (DOWNLOAD_DATE - inspected).dt.days
    df["rating_date"] = inspected.dt.strftime("%Y-%m-%d")
    return df


frames = [read_fsa_xml(f, city, borough) for f, (city, borough) in SOURCES.items()]
df = tidy(pd.concat(frames, ignore_index=True))
df = df.drop_duplicates(subset=["business_id"])

csv_path = PROCESSED / "food_hygiene_cleaned.csv"
db_path = PROCESSED / "food_hygiene.db"

df.to_csv(csv_path, index=False)

with sqlite3.connect(db_path) as conn:
    df.to_sql("establishments", conn, if_exists="replace", index=False)

print("Data cleaning completed!")
print(df.groupby("borough").size().rename("records").to_string())
print(f"\nCombined unique records: {len(df):,}")
print("\nRating status by city:")
print(pd.crosstab(df["city"], df["rating_status"]).to_string())
print(f"\nDatabase saved to: {db_path}")