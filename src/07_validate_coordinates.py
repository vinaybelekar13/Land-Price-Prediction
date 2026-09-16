import pandas as pd

INPUT = "data/location_coordinates.csv"
OUTPUT = "data/validated_location_coordinates.csv"

df = pd.read_csv(INPUT)

# Bengaluru study-area bounds
VALID = (
    df["latitude"].between(12.70, 13.25)
    & df["longitude"].between(77.35, 77.85)
)

# Keep only valid coordinates
validated = df[VALID].copy()

# Remove duplicate locality names
validated = validated.drop_duplicates(
    subset=["location"],
    keep="first"
)

validated.to_csv(OUTPUT, index=False)

print("===================================")
print("COORDINATE VALIDATION COMPLETE")
print("===================================")
print("Original:", len(df))
print("Valid:", len(validated))
print("Rejected:", len(df) - len(validated))
print("Saved:", OUTPUT)