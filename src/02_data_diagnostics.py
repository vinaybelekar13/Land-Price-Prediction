import pandas as pd

FILE_PATH = "data/bengaluru_house_prices.csv"

df = pd.read_csv(FILE_PATH)

print("=" * 70)
print("DATA DIAGNOSTICS")
print("=" * 70)

# --------------------------------------------------
# 1. SIZE VALUES
# --------------------------------------------------

print("\n1. SIZE VALUES")
print("-" * 70)

print("Unique size values:")
print(df["size"].value_counts().to_string())


# --------------------------------------------------
# 2. TOTAL SQFT VALUES
# --------------------------------------------------

print("\n2. TOTAL SQFT VALUES")
print("-" * 70)

print("Examples of total_sqft values:")
print(df["total_sqft"].head(30).to_string(index=False))

range_values = df[
    df["total_sqft"].astype(str).str.contains("-", regex=False)
]["total_sqft"]

print("\nNumber of sqft range values:", len(range_values))

print("\nExamples of sqft ranges:")
print(range_values.head(20).to_string(index=False))


# --------------------------------------------------
# 3. BATHROOM VALUES
# --------------------------------------------------

print("\n3. BATHROOM VALUES")
print("-" * 70)

print(df["bath"].value_counts(dropna=False).sort_index().to_string())


# --------------------------------------------------
# 4. BALCONY VALUES
# --------------------------------------------------

print("\n4. BALCONY VALUES")
print("-" * 70)

print(df["balcony"].value_counts(dropna=False).sort_index().to_string())


# --------------------------------------------------
# 5. AREA TYPE
# --------------------------------------------------

print("\n5. AREA TYPE")
print("-" * 70)

print(df["area_type"].value_counts().to_string())


# --------------------------------------------------
# 6. AVAILABILITY
# --------------------------------------------------

print("\n6. AVAILABILITY")
print("-" * 70)

print(df["availability"].value_counts().head(20).to_string())


# --------------------------------------------------
# 7. PRICE
# --------------------------------------------------

print("\n7. PRICE RANGE")
print("-" * 70)

print("Minimum price:", df["price"].min(), "Lakhs")
print("Maximum price:", df["price"].max(), "Lakhs")


# --------------------------------------------------
# 8. LOCATION
# --------------------------------------------------

print("\n8. LOCATION")
print("-" * 70)

print("Unique locations:", df["location"].nunique())
print("Missing locations:", df["location"].isna().sum())

print("\nLocations with fewer than 5 properties:")
print(
    (df["location"].value_counts() < 5).sum()
)


# --------------------------------------------------
# 9. DUPLICATES
# --------------------------------------------------

print("\n9. DUPLICATES")
print("-" * 70)

print("Duplicate rows:", df.duplicated().sum())


print("\n" + "=" * 70)
print("DIAGNOSTICS COMPLETE")
print("=" * 70)