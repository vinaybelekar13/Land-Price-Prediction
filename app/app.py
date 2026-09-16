from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import joblib
import os

app = Flask(__name__)

# =========================================================
# LOAD MODEL AND DATA
# =========================================================

MODEL_PATH = "models/xgboost.pkl"
COORD_PATH = "data/validated_location_coordinates.csv"
AMENITY_PATH = "data/bengaluru_amenities.csv"

model = joblib.load(MODEL_PATH)

coords = pd.read_csv(COORD_PATH)
amenities = pd.read_csv(AMENITY_PATH)

# Remove duplicate locality coordinates
coords = coords.drop_duplicates("location").reset_index(drop=True)

# =========================================================
# HAVERSINE DISTANCE
# =========================================================

def haversine(lat1, lon1, lat2, lon2):

    R = 6371.0

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1)
        * np.cos(lat2)
        * np.sin(dlon / 2) ** 2
    )

    return 2 * R * np.arcsin(np.sqrt(a))


# =========================================================
# FIND NEAREST AMENITY
# =========================================================

def nearest_distance(lat, lon, category):

    data = amenities[
        amenities["category"] == category
    ][["latitude", "longitude"]].dropna()

    if data.empty:
        return float(amenities["latitude"].median())

    distances = haversine(
        lat,
        lon,
        data["latitude"].values,
        data["longitude"].values
    )

    return float(np.min(distances))


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def index():

    locations = sorted(
        coords["location"].dropna().unique()
    )

    return render_template(
        "index.html",
        locations=locations
    )


# =========================================================
# PREDICTION API
# =========================================================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        data = request.get_json()

        location = data["location"]

        bhk = float(data["bhk"])
        total_sqft = float(data["total_sqft"])
        bath = float(data["bath"])
        balcony = float(data["balcony"])

        # -------------------------------------------------
        # Find selected locality
        # -------------------------------------------------

        row = coords[
            coords["location"] == location
        ]

        if row.empty:
            return jsonify({
                "error": "Location not available in validated Bengaluru dataset."
            }), 400

        lat = float(row.iloc[0]["latitude"])
        lon = float(row.iloc[0]["longitude"])

        # -------------------------------------------------
        # Amenity distances
        # -------------------------------------------------

        distances = {}

        categories = [
            "school",
            "hospital",
            "college",
            "bus_stop",
            "railway_station",
            "shopping",
            "bank",
            "park"
        ]

        for category in categories:

            distances[category] = nearest_distance(
                lat,
                lon,
                category
            )

        # -------------------------------------------------
        # Model input
        # -------------------------------------------------

        input_data = pd.DataFrame([{

            "area_type": "Super built-up Area",

            "availability": "Ready To Move",

            "location": location,

            "bhk": bhk,

            "total_sqft": total_sqft,

            "bath": bath,

            "balcony": balcony,

            "latitude": lat,

            "longitude": lon,

            "distance_school_km":
                distances["school"],

            "distance_hospital_km":
                distances["hospital"],

            "distance_college_km":
                distances["college"],

            "distance_bus_stop_km":
                distances["bus_stop"],

            "distance_railway_station_km":
                distances["railway_station"],

            "distance_shopping_km":
                distances["shopping"],

            "distance_bank_km":
                distances["bank"],

            "distance_park_km":
                distances["park"]

        }])

        # -------------------------------------------------
        # Prediction
        # -------------------------------------------------

        prediction = float(
            model.predict(input_data)[0]
        )

        return jsonify({

            "success": True,

            "location": location,

            "latitude": lat,

            "longitude": lon,

            "predicted_price": round(
                prediction,
                2
            ),

            "amenities": {

                "School":
                    round(distances["school"], 2),

                "Hospital":
                    round(distances["hospital"], 2),

                "College":
                    round(distances["college"], 2),

                "Bus Stop":
                    round(distances["bus_stop"], 2),

                "Railway Station":
                    round(distances["railway_station"], 2),

                "Shopping":
                    round(distances["shopping"], 2),

                "Bank":
                    round(distances["bank"], 2),

                "Park":
                    round(distances["park"], 2)
            }

        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )