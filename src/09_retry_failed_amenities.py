import pandas as pd
import requests
import time
import os

INPUT_FILE = "data/validated_location_coordinates.csv"
EXISTING_FILE = "data/bengaluru_amenities.csv"
OUTPUT_FILE = "data/bengaluru_amenities_complete.csv"

locations = pd.read_csv(INPUT_FILE)

min_lat = locations["latitude"].min()
max_lat = locations["latitude"].max()
min_lon = locations["longitude"].min()
max_lon = locations["longitude"].max()

lat_step = (max_lat - min_lat) / 3
lon_step = (max_lon - min_lon) / 3

# Only failed grids: 3, 6, 9
failed_grids = [3, 6, 9]

OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

session = requests.Session()
session.headers.update({
    "User-Agent": "Bengaluru-Land-Price-Prediction-Project/1.0"
})

new_amenities = []

for grid_number in failed_grids:

    i = (grid_number - 1) // 3
    j = (grid_number - 1) % 3

    south = min_lat + i * lat_step
    north = min_lat + (i + 1) * lat_step
    west = min_lon + j * lon_step
    east = min_lon + (j + 1) * lon_step

    print("\n===================================")
    print(f"RETRYING GRID {grid_number}")
    print("===================================")
    print(f"Bounds: {south:.5f},{west:.5f},{north:.5f},{east:.5f}")

    query = f"""
    [out:json][timeout:180];

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

    for server in OVERPASS_SERVERS:

        try:
            print(f"\nTrying server: {server}")

            response = session.post(
                server,
                data=query,
                timeout=240
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
                    new_amenities.append({
                        "name": tags.get("name", "Unnamed"),
                        "category": category,
                        "latitude": lat,
                        "longitude": lon
                    })

            success = True
            break

        except Exception as e:
            print("Failed:", e)
            print("Trying next server...")
            time.sleep(15)

    if not success:
        print(f"WARNING: Grid {grid_number} could not be collected.")

    time.sleep(15)


# Load existing amenities
existing = pd.read_csv(EXISTING_FILE)

print("\nExisting amenities:", len(existing))
print("New amenities:", len(new_amenities))

new_df = pd.DataFrame(new_amenities)

if not new_df.empty:

    combined = pd.concat(
        [existing, new_df],
        ignore_index=True
    )

else:

    combined = existing.copy()

# Remove duplicates
combined = combined.drop_duplicates(
    subset=["category", "latitude", "longitude"]
).reset_index(drop=True)

combined.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n===================================")
print("AMENITY DATA MERGED")
print("===================================")

print("Final amenities:", len(combined))

print("\nAmenities by category:")
print(combined["category"].value_counts())

print("\nSaved:", OUTPUT_FILE)