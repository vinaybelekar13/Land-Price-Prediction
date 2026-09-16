import pandas as pd
import requests
import time
import os

INPUT_FILE = "data/validated_location_coordinates.csv"
OUTPUT_FILE = "data/bengaluru_amenities.csv"

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

locations = pd.read_csv(INPUT_FILE)

print("Locations:", len(locations))

# Study-area bounds
min_lat = locations["latitude"].min()
max_lat = locations["latitude"].max()
min_lon = locations["longitude"].min()
max_lon = locations["longitude"].max()

print(f"Latitude range: {min_lat} to {max_lat}")
print(f"Longitude range: {min_lon} to {max_lon}")

# Split Bengaluru into a 3 x 3 grid
lat_step = (max_lat - min_lat) / 3
lon_step = (max_lon - min_lon) / 3

all_amenities = []

session = requests.Session()
session.headers.update({
    "User-Agent": "Bengaluru-Land-Price-Prediction-Project/1.0"
})

for i in range(3):
    for j in range(3):

        south = min_lat + i * lat_step
        north = min_lat + (i + 1) * lat_step
        west = min_lon + j * lon_step
        east = min_lon + (j + 1) * lon_step

        print(f"\nQuerying grid {i*3+j+1}/9...")
        print(f"Bounds: {south:.5f},{west:.5f},{north:.5f},{east:.5f}")

        query = f"""
        [out:json][timeout:120];

        (
          node["amenity"="school"]({south},{west},{north},{east});
          way["amenity"="school"]({south},{west},{north},{east});

          node["amenity"="college"]({south},{west},{north},{east});
          way["amenity"="college"]({south},{west},{north},{east});

          node["amenity"="university"]({south},{west},{north},{east});
          way["amenity"="university"]({south},{west},{north},{east});

          node["amenity"="hospital"]({south},{west},{north},{east});
          way["amenity"="hospital"]({south},{west},{north},{east});

          node["highway"="bus_stop"]({south},{west},{north},{east});

          node["railway"="station"]({south},{west},{north},{east});
          node["railway"="halt"]({south},{west},{north},{east});

          node["shop"="supermarket"]({south},{west},{north},{east});
          way["shop"="supermarket"]({south},{west},{north},{east});

          node["shop"="mall"]({south},{west},{north},{east});
          way["shop"="mall"]({south},{west},{north},{east});

          node["amenity"="bank"]({south},{west},{north},{east});
          way["amenity"="bank"]({south},{west},{north},{east});

          node["leisure"="park"]({south},{west},{north},{east});
          way["leisure"="park"]({south},{west},{north},{east});
        );

        out center;
        """

        success = False

        for attempt in range(3):

            try:
                response = session.post(
                    OVERPASS_URL,
                    data=query,
                    timeout=180
                )

                response.raise_for_status()

                data = response.json()

                elements = data.get("elements", [])

                print("Elements received:", len(elements))

                for element in elements:

                    tags = element.get("tags", {})

                    if element["type"] == "node":
                        lat = element.get("lat")
                        lon = element.get("lon")
                    else:
                        center = element.get("center", {})
                        lat = center.get("lat")
                        lon = center.get("lon")

                    if lat is None or lon is None:
                        continue

                    category = None

                    if tags.get("amenity") == "school":
                        category = "school"

                    elif tags.get("amenity") in ["college", "university"]:
                        category = "college"

                    elif tags.get("amenity") == "hospital":
                        category = "hospital"

                    elif tags.get("highway") == "bus_stop":
                        category = "bus_stop"

                    elif tags.get("railway") in ["station", "halt"]:
                        category = "railway_station"

                    elif tags.get("shop") in ["supermarket", "mall"]:
                        category = "shopping"

                    elif tags.get("amenity") == "bank":
                        category = "bank"

                    elif tags.get("leisure") == "park":
                        category = "park"

                    if category:

                        all_amenities.append({
                            "name": tags.get("name", "Unnamed"),
                            "category": category,
                            "latitude": lat,
                            "longitude": lon
                        })

                success = True
                break

            except Exception as e:

                print(f"Attempt {attempt + 1} failed:", e)

                if attempt < 2:
                    print("Retrying in 10 seconds...")
                    time.sleep(10)

        if not success:
            print("WARNING: Grid failed after 3 attempts.")

        # Be polite to the public Overpass server
        time.sleep(5)


# Create dataframe
amenities_df = pd.DataFrame(all_amenities)

if amenities_df.empty:
    print("\nNo amenities collected.")
    raise SystemExit

# Remove duplicate amenities
amenities_df = amenities_df.drop_duplicates(
    subset=["category", "latitude", "longitude"]
)

os.makedirs("data", exist_ok=True)

amenities_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n===================================")
print("AMENITY COLLECTION COMPLETE")
print("===================================")

print("Total amenities:", len(amenities_df))

print("\nAmenities by category:")
print(amenities_df["category"].value_counts())

print("\nSaved:", OUTPUT_FILE)