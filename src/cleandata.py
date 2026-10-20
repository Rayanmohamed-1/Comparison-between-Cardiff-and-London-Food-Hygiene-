from pathlib import Path
import sqlite3
import xml.etree.ElementTree as ET

import pandas as pd

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"

PROCESSED.mkdir(parents=True, exist_ok=True)


def read_fsa_xml(filename, location):
    root = ET.parse(RAW / filename).getroot()
    records = []

    for business in root.findall(".//EstablishmentDetail"):
        def get(field):
            return business.findtext(field)

        scores = business.find("Scores")

        def score(field):
            return scores.findtext(field) if scores is not None else None

        records.append({
            "business_id": get("FHRSID"),
            "business_name": get("BusinessName"),
            "business_type": get("BusinessType"),
            "rating": get("RatingValue"),
            "rating_date": get("RatingDate"),
            "hygiene": score("Hygiene"),
            "structural": score("Structural"),
            "management": score("ConfidenceInManagement"),
            "postcode": get("PostCode"),
            "location": location
        })

    df = pd.DataFrame(records)

    if df.empty:
        raise ValueError(f"No establishments found in {filename}")

    for column in ["rating", "hygiene", "structural", "management"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["rating_date"] = pd.to_datetime(
        df["rating_date"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    return df


cardiff = read_fsa_xml("cardiff.xml", "Cardiff")
westminster = read_fsa_xml("westminster.xml", "Westminster")

df = pd.concat([cardiff, westminster], ignore_index=True)

df = df.drop_duplicates(subset=["business_id"])

csv_path = PROCESSED / "food_hygiene_cleaned.csv"
db_path = PROCESSED / "food_hygiene.db"

df.to_csv(csv_path, index=False)

with sqlite3.connect(db_path) as conn:
    df.to_sql(
        "establishments",
        conn,
        if_exists="replace",
        index=False
    )

print("Data cleaning completed!")
print(f"Cardiff: {len(cardiff):,} records")
print(f"Westminster: {len(westminster):,} records")
print(f"Combined unique records: {len(df):,}")
print(f"Missing ratings: {df['rating'].isna().sum():,}")
print(f"Database saved to: {db_path}")
print("\nRating distribution:")
print(df.groupby(["location", "rating"]).size())
