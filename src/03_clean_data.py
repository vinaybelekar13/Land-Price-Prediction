import pandas as pd
import numpy as np

# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "data/bengaluru_house_prices.csv"
OUTPUT_FILE = "data/cleaned_bengaluru_house_prices.csv"


# ============================================================
# 1. LOAD DATA
# ============================================================

print("=" * 70)
print("BENGALURU HOUSE PRICE DATA CLEANING")
print("=" * 70)

df = pd.read_csv(INPUT_FILE)

print("\nOriginal dataset shape:")
print(df.shape)


# ============================================================
# 2. REMOVE DUPLICATES
# ============================================================

duplicates = df.duplicated().sum()

print("\nDuplicate rows found:", duplicates)

df = df.drop_duplicates().copy()

print("Shape after removing duplicates:")
print(df.shape)


# ============================================================
# 3. CLEAN COLUMN NAMES
# ============================================================

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

print("\nColumns after standardization:")
print(df.columns.tolist())


# ============================================================
# 4. CLEAN LOCATION
# ============================================================

# Remove leading/trailing spaces
df["location"] = df["location"].astype("string").str.strip()

# Remove the one missing location
missing_location = df["location"].isna().sum()

print("\nMissing locations:", missing_location)

df = df.dropna(subset=["location"]).copy()


# ============================================================
# 5. CLEAN SIZE → BHK
# ============================================================

# Example:
# "2 BHK"       → 2
# "4 Bedroom"   → 4
# "1 RK"        → 1

df["bhk"] = (
    df["size"]
    .astype("string")
    .str.extract(r"(\d+)", expand=False)
)

df["bhk"] = pd.to_numeric(df["bhk"], errors="coerce")

print("\nBHK values after conversion:")
print(df["bhk"].value_counts().sort_index().to_string())


# ============================================================
# 6. CLEAN TOTAL SQFT
# ============================================================

def convert_sqft(value):

    value = str(value).strip()

    # Handle ranges such as:
    # 2100 - 2850
    if "-" in value:

        parts = value.split("-")

        try:
            low = float(parts[0].strip())
            high = float(parts[1].strip())

            return (low + high) / 2

        except ValueError:
            return np.nan

    # Handle normal numeric values
    try:
        return float(value)

    except ValueError:
        return np.nan


df["total_sqft"] = df["total_sqft"].apply(convert_sqft)

df["total_sqft"] = pd.to_numeric(
    df["total_sqft"],
    errors="coerce"
)

print("\nMissing total_sqft after conversion:")
print(df["total_sqft"].isna().sum())


# ============================================================
# 7. CONVERT BATHROOM AND BALCONY TO NUMERIC
# ============================================================

df["bath"] = pd.to_numeric(
    df["bath"],
    errors="coerce"
)

df["balcony"] = pd.to_numeric(
    df["balcony"],
    errors="coerce"
)


# ============================================================
# 8. HANDLE MISSING BATHROOM VALUES
# ============================================================

# Fill missing bathroom values using the median
# bathroom count.

bath_median = df["bath"].median()

print("\nBathroom median:", bath_median)

df["bath"] = df["bath"].fillna(bath_median)


# ============================================================
# 9. HANDLE MISSING BALCONY VALUES
# ============================================================

balcony_median = df["balcony"].median()

print("Balcony median:", balcony_median)

df["balcony"] = df["balcony"].fillna(balcony_median)


# ============================================================
# 10. REMOVE ROWS WITH INVALID CORE VALUES
# ============================================================

before = len(df)

df = df.dropna(
    subset=[
        "bhk",
        "total_sqft",
        "price"
    ]
).copy()

print("\nRows removed because of missing core values:")
print(before - len(df))


# ============================================================
# 11. CREATE PRICE PER SQFT
# ============================================================

df["price_per_sqft"] = (
    df["price"] * 100000
) / df["total_sqft"]


# ============================================================
# 12. BASIC VALIDITY FILTERS
# ============================================================

before = len(df)

# Property must have positive area
df = df[df["total_sqft"] > 0]

# Property must have positive BHK
df = df[df["bhk"] > 0]

# Price must be positive
df = df[df["price"] > 0]

print("\nRows removed by basic validity checks:")
print(before - len(df))


# ============================================================
# 13. CREATE CLEAN DATASET
# ============================================================

# We no longer need the raw size column.
df = df.drop(columns=["size"])

# Society has too many missing values and is not required
# for our spatial ML approach.
df = df.drop(columns=["society"])


# ============================================================
# 14. REORDER IMPORTANT COLUMNS
# ============================================================

preferred_columns = [
    "area_type",
    "availability",
    "location",
    "bhk",
    "total_sqft",
    "bath",
    "balcony",
    "price_per_sqft",
    "price"
]

df = df[
    [col for col in preferred_columns if col in df.columns]
]


# ============================================================
# 15. SAVE CLEAN DATASET
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# 16. FINAL REPORT
# ============================================================

print("\n" + "=" * 70)
print("CLEANING COMPLETE")
print("=" * 70)

print("\nFinal dataset shape:")
print(df.shape)

print("\nFinal columns:")
print(df.columns.tolist())

print("\nRemaining missing values:")
print(df.isnull().sum().to_string())

print("\nDuplicate rows remaining:")
print(df.duplicated().sum())

print("\nFirst 5 rows:")
print(df.head().to_string())

print("\nSaved to:")
print(OUTPUT_FILE)

print("\n" + "=" * 70)