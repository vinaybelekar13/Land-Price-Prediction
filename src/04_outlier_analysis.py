import pandas as pd
import numpy as np

INPUT_FILE = "data/cleaned_bengaluru_house_prices.csv"

df = pd.read_csv(INPUT_FILE)

print("=" * 75)
print("OUTLIER ANALYSIS")
print("=" * 75)

print("\nDataset shape:", df.shape)


# ============================================================
# 1. BASIC STATISTICS
# ============================================================

print("\n1. BASIC STATISTICS")
print("-" * 75)

columns = [
    "bhk",
    "total_sqft",
    "bath",
    "balcony",
    "price_per_sqft",
    "price"
]

print(df[columns].describe().to_string())


# ============================================================
# 2. PERCENTILES
# ============================================================

print("\n2. IMPORTANT PERCENTILES")
print("-" * 75)

for column in columns:

    print(f"\n{column}")

    percentiles = df[column].quantile(
        [0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99]
    )

    print(percentiles.to_string())


# ============================================================
# 3. BHK DISTRIBUTION
# ============================================================

print("\n3. BHK DISTRIBUTION")
print("-" * 75)

print(
    df["bhk"]
    .value_counts()
    .sort_index()
    .to_string()
)


# ============================================================
# 4. VERY LARGE BHK VALUES
# ============================================================

print("\n4. PROPERTIES WITH BHK >= 10")
print("-" * 75)

large_bhk = df[df["bhk"] >= 10][
    [
        "location",
        "bhk",
        "total_sqft",
        "bath",
        "price"
    ]
]

print(large_bhk.to_string(index=False))


# ============================================================
# 5. SQFT PER BHK
# ============================================================

df["sqft_per_bhk"] = df["total_sqft"] / df["bhk"]

print("\n5. SQFT PER BHK")
print("-" * 75)

print(
    df["sqft_per_bhk"]
    .describe(
        percentiles=[
            0.01,
            0.05,
            0.25,
            0.50,
            0.75,
            0.95,
            0.99
        ]
    )
    .to_string()
)


# ============================================================
# 6. SUSPICIOUSLY LOW SQFT PER BHK
# ============================================================

print("\n6. SQFT/BHK < 300")
print("-" * 75)

low_sqft = df[df["sqft_per_bhk"] < 300][
    [
        "location",
        "bhk",
        "total_sqft",
        "sqft_per_bhk",
        "bath",
        "price"
    ]
]

print("Count:", len(low_sqft))

print("\nExamples:")
print(low_sqft.head(30).to_string(index=False))


# ============================================================
# 7. SUSPICIOUSLY HIGH SQFT PER BHK
# ============================================================

print("\n7. SQFT/BHK > 5000")
print("-" * 75)

high_sqft = df[df["sqft_per_bhk"] > 5000][
    [
        "location",
        "bhk",
        "total_sqft",
        "sqft_per_bhk",
        "bath",
        "price"
    ]
]

print("Count:", len(high_sqft))

print("\nExamples:")
print(high_sqft.head(30).to_string(index=False))


# ============================================================
# 8. BATHROOM VS BHK
# ============================================================

print("\n8. BATHROOMS GREATER THAN BHK + 2")
print("-" * 75)

bath_issue = df[
    df["bath"] > df["bhk"] + 2
][
    [
        "location",
        "bhk",
        "bath",
        "total_sqft",
        "price"
    ]
]

print("Count:", len(bath_issue))

print("\nExamples:")
print(bath_issue.head(30).to_string(index=False))


# ============================================================
# 9. PRICE PER SQFT EXTREMES
# ============================================================

print("\n9. PRICE PER SQFT EXTREMES")
print("-" * 75)

print("Lowest 20:")
print(
    df[
        [
            "location",
            "total_sqft",
            "bhk",
            "price_per_sqft",
            "price"
        ]
    ]
    .sort_values("price_per_sqft")
    .head(20)
    .to_string(index=False)
)

print("\nHighest 20:")
print(
    df[
        [
            "location",
            "total_sqft",
            "bhk",
            "price_per_sqft",
            "price"
        ]
    ]
    .sort_values("price_per_sqft", ascending=False)
    .head(20)
    .to_string(index=False)
)


# ============================================================
# 10. EXTREME PRICE VALUES
# ============================================================

print("\n10. HIGHEST PRICE PROPERTIES")
print("-" * 75)

print(
    df[
        [
            "location",
            "bhk",
            "total_sqft",
            "bath",
            "price",
            "price_per_sqft"
        ]
    ]
    .sort_values("price", ascending=False)
    .head(20)
    .to_string(index=False)
)


# ============================================================
# 11. DUPLICATES AFTER TRANSFORMATION
# ============================================================

print("\n11. DUPLICATES")
print("-" * 75)

print(
    "Duplicate rows:",
    df.duplicated().sum()
)


print("\n" + "=" * 75)
print("OUTLIER ANALYSIS COMPLETE")
print("=" * 75)