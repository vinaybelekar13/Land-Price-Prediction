import pandas as pd
import numpy as np

INPUT_FILE = "data/cleaned_bengaluru_house_prices.csv"
OUTPUT_FILE = "data/final_cleaned_bengaluru_house_prices.csv"

print("=" * 75)
print("FINAL OUTLIER CLEANING")
print("=" * 75)

# ============================================================
# 1. LOAD DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)

print("\nOriginal cleaned dataset:", df.shape)


# ============================================================
# 2. REMOVE DUPLICATES CREATED AFTER TRANSFORMATION
# ============================================================

before = len(df)

df = df.drop_duplicates().copy()

print("\nDuplicates removed:", before - len(df))
print("Shape:", df.shape)


# ============================================================
# 3. CREATE SQFT PER BHK
# ============================================================

df["sqft_per_bhk"] = df["total_sqft"] / df["bhk"]


# ============================================================
# 4. REMOVE IMPOSSIBLE / EXTREME AREA-BHK COMBINATIONS
# ============================================================

before = len(df)

# A residential property should have a reasonable
# amount of floor area per bedroom.
#
# This removes obvious data-entry anomalies such as:
# 43 BHK / 2400 sqft
# 27 BHK / 8000 sqft
# 1 BHK / 1 sqft
#
# We use 300 sqft per BHK as a conservative
# data-quality threshold.

df = df[df["sqft_per_bhk"] >= 300].copy()

print("\nRemoved because sqft_per_bhk < 300:")
print(before - len(df))
print("Shape:", df.shape)


# ============================================================
# 5. REMOVE EXTREMELY LARGE AREA/BHK VALUES
# ============================================================

before = len(df)

df = df[df["sqft_per_bhk"] <= 5000].copy()

print("\nRemoved because sqft_per_bhk > 5000:")
print(before - len(df))
print("Shape:", df.shape)


# ============================================================
# 6. REMOVE EXTREME BATHROOM/BHK COMBINATIONS
# ============================================================

before = len(df)

# A property having more than BHK + 2 bathrooms
# is treated as a potential data-quality anomaly.

df = df[
    df["bath"] <= df["bhk"] + 2
].copy()

print("\nRemoved because bath > bhk + 2:")
print(before - len(df))
print("Shape:", df.shape)


# ============================================================
# 7. PRICE PER SQFT OUTLIER HANDLING
# ============================================================

# IMPORTANT:
# price_per_sqft is used ONLY for cleaning.
# It will NOT be used as an ML input feature.

print("\nPrice per sqft before filtering:")
print(df["price_per_sqft"].describe().to_string())


# ------------------------------------------------------------
# Location-level filtering
# ------------------------------------------------------------
#
# Locations with enough observations get their own
# 1st and 99th percentile limits.
#
# Sparse locations are left untouched rather than
# making unreliable assumptions.

location_counts = df["location"].value_counts()

locations_with_enough_data = location_counts[
    location_counts >= 10
].index

mask_common_locations = df["location"].isin(
    locations_with_enough_data
)

common_df = df[mask_common_locations].copy()

# Calculate location-level 1st and 99th percentiles
location_lower = common_df.groupby("location")[
    "price_per_sqft"
].transform("quantile", 0.01)

location_upper = common_df.groupby("location")[
    "price_per_sqft"
].transform("quantile", 0.99)

common_df = common_df[
    (common_df["price_per_sqft"] >= location_lower) &
    (common_df["price_per_sqft"] <= location_upper)
].copy()

# Keep sparse locations unchanged
sparse_df = df[~mask_common_locations].copy()

before = len(df)

df = pd.concat(
    [common_df, sparse_df],
    ignore_index=True
)

print("\nRows removed by location-level price/sqft filtering:")
print(before - len(df))

print("Shape:", df.shape)


# ============================================================
# 8. REMOVE PRICE PER SQFT FEATURE
# ============================================================

# price_per_sqft contains PRICE information.
# PRICE is our prediction target.
#
# Keeping this feature for ML would cause target leakage.

df = df.drop(columns=["price_per_sqft"])


# ============================================================
# 9. REMOVE TEMPORARY FEATURE
# ============================================================

df = df.drop(columns=["sqft_per_bhk"])


# ============================================================
# 10. FINAL COLUMN ORDER
# ============================================================

columns = [
    "area_type",
    "availability",
    "location",
    "bhk",
    "total_sqft",
    "bath",
    "balcony",
    "price"
]

df = df[columns]


# ============================================================
# 11. FINAL VALIDATION
# ============================================================

print("\n" + "=" * 75)
print("FINAL DATASET VALIDATION")
print("=" * 75)

print("\nFinal shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isnull().sum().to_string())

print("\nDuplicate rows:")
print(df.duplicated().sum())

print("\nBHK range:")
print(df["bhk"].min(), "to", df["bhk"].max())

print("\nTotal sqft range:")
print(df["total_sqft"].min(), "to", df["total_sqft"].max())

print("\nPrice range:")
print(df["price"].min(), "to", df["price"].max(), "Lakhs")

print("\nFinal descriptive statistics:")
print(
    df[
        ["bhk", "total_sqft", "bath", "balcony", "price"]
    ].describe().to_string()
)


# ============================================================
# 12. SAVE FINAL DATASET
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nSaved final dataset to:")
print(OUTPUT_FILE)

print("\n" + "=" * 75)
print("FINAL CLEANING COMPLETE")
print("=" * 75)