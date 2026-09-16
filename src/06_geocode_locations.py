import pandas as pd
import os
import time
import re
from geopy.geocoders import Nominatim

INPUT = "data/final_cleaned_bengaluru_house_prices.csv"
OUTPUT = "data/location_coordinates.csv"

df = pd.read_csv(INPUT)

# All unique locations
locations = (
    df["location"]
    .dropna()
    .astype(str)
    .str.strip()
    .drop_duplicates()
    .tolist()
)

# Load existing results
if os.path.exists(OUTPUT):
    coords = pd.read_csv(OUTPUT)
else:
    coords = pd.DataFrame(
        columns=["location", "latitude", "longitude", "address"]
    )

# Existing locations
done = set(coords["location"].astype(str))

# Only process remaining locations
remaining = [x for x in locations if x not in done]

print(f"Total locations: {len(locations)}")
print(f"Already processed: {len(done)}")
print(f"Remaining: {len(remaining)}")
print()

geolocator = Nominatim(
    user_agent="vinay_land_price_prediction_group26"
)


def clean_location(name):
    """Clean common formatting problems."""

    name = str(name).strip()

    # Remove leading numbers such as:
    # 1 Giri Nagar -> Giri Nagar
    name = re.sub(r"^\d+\s*", "", name)

    # Fix missing spaces after numbers
    name = re.sub(r"^\d+", "", name)

    # Normalize common spelling
    replacements = {
        "banshankari": "banashankari",
        "Banshankari": "Banashankari",
        "electronic city phase 1": "Electronics City Phase 1",
        "electronic city phase ii": "Electronic City Phase II",
        "hrbr": "HRBR",
    }

    for old, new in replacements.items():
        name = name.replace(old, new)

    name = re.sub(r"\s+", " ", name)

    return name.strip()


for index, location in enumerate(remaining, 1):

    cleaned = clean_location(location)

    queries = [
        f"{cleaned}, Bengaluru, Karnataka, India",
        f"{cleaned}, Bangalore, Karnataka, India",
        f"{cleaned}, Karnataka, India",
    ]

    result = None

    for query in queries:

        try:
            result = geolocator.geocode(
                query,
                exactly_one=True,
                timeout=8
            )

            if result:
                break

        except Exception:
            pass

    if result:

        lat = result.latitude
        lon = result.longitude
        address = result.address

        print(
            f"[{index}/{len(remaining)}] "
            f"FOUND: {location} -> "
            f"{lat:.6f}, {lon:.6f}"
        )

    else:

        lat = None
        lon = None
        address = None

        print(
            f"[{index}/{len(remaining)}] "
            f"NOT FOUND: {location}"
        )

    new_row = pd.DataFrame([{
        "location": location,
        "latitude": lat,
        "longitude": lon,
        "address": address
    }])

    coords = pd.concat(
        [coords, new_row],
        ignore_index=True
    )

    # Save after every location
    coords.to_csv(OUTPUT, index=False)

    # Nominatim rate limit
    time.sleep(1.1)


print("\n===================================")
print("GEOCODING COMPLETE")
print("===================================")

print("Total:", len(coords))
print("Found:", coords["latitude"].notna().sum())
print("Not found:", coords["latitude"].isna().sum())

print("\nSaved:")
print(OUTPUT)