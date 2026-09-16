import pandas as pd
import numpy as np
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from xgboost import XGBRegressor


# ============================================================
# FILES
# ============================================================

PROPERTY_FILE = "data/final_cleaned_bengaluru_house_prices.csv"
COORD_FILE = "data/validated_location_coordinates.csv"
AMENITY_FILE = "data/bengaluru_amenities.csv"

FINAL_DATASET = "data/final_gis_dataset.csv"
RESULT_FILE = "results/model_comparison.csv"


os.makedirs("data", exist_ok=True)
os.makedirs("models", exist_ok=True)
os.makedirs("results", exist_ok=True)


# ============================================================
# 1. LOAD DATA
# ============================================================

print("\nLoading datasets...")

properties = pd.read_csv(PROPERTY_FILE)
coords = pd.read_csv(COORD_FILE)
amenities = pd.read_csv(AMENITY_FILE)

print("Properties:", len(properties))
print("Coordinates:", len(coords))
print("Amenities:", len(amenities))


# ============================================================
# 2. MERGE PROPERTY + COORDINATES
# ============================================================

df = properties.merge(
    coords[["location", "latitude", "longitude"]],
    on="location",
    how="inner"
)

print("\nProperties with coordinates:", len(df))


# ============================================================
# 3. CALCULATE DISTANCES
# ============================================================

print("\nCalculating nearest amenity distances...")


def haversine_vectorized(lat1, lon1, lat2, lon2):

    R = 6371.0

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    )

    return 2 * R * np.arcsin(np.sqrt(a))


amenity_categories = [
    "school",
    "hospital",
    "college",
    "bus_stop",
    "railway_station",
    "shopping",
    "bank",
    "park"
]


for category in amenity_categories:

    print(f"  Processing {category}...")

    a = amenities[
        amenities["category"] == category
    ][["latitude", "longitude"]].dropna()

    if len(a) == 0:
        df[f"distance_{category}_km"] = np.nan
        continue

    amenity_lat = a["latitude"].values
    amenity_lon = a["longitude"].values

    distances = []

    # Process property by property to control memory
    for lat, lon in zip(
        df["latitude"].values,
        df["longitude"].values
    ):

        d = haversine_vectorized(
            lat,
            lon,
            amenity_lat,
            amenity_lon
        )

        distances.append(np.min(d))

    df[f"distance_{category}_km"] = distances


# ============================================================
# 4. REMOVE EXTREME DISTANCE VALUES
# ============================================================

distance_columns = [
    f"distance_{x}_km"
    for x in amenity_categories
]

# Fill missing distances using the median
for col in distance_columns:

    median_value = df[col].median()

    df[col] = df[col].fillna(median_value)


# ============================================================
# 5. SAVE GIS DATASET
# ============================================================

df.to_csv(
    FINAL_DATASET,
    index=False
)

print("\n===================================")
print("GIS DATASET CREATED")
print("===================================")

print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nDistance feature summary:")
print(df[distance_columns].describe().T)


# ============================================================
# 6. PREPARE ML DATA
# ============================================================

target = "price"

features = [
    "area_type",
    "availability",
    "location",
    "bhk",
    "total_sqft",
    "bath",
    "balcony",
    "latitude",
    "longitude",
    "distance_school_km",
    "distance_hospital_km",
    "distance_college_km",
    "distance_bus_stop_km",
    "distance_railway_station_km",
    "distance_shopping_km",
    "distance_bank_km",
    "distance_park_km"
]

X = df[features]
y = df[target]


# ============================================================
# 7. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("\nTraining rows:", len(X_train))
print("Testing rows:", len(X_test))


# ============================================================
# 8. PREPROCESSING
# ============================================================

categorical_features = [
    "area_type",
    "availability",
    "location"
]

numeric_features = [
    "bhk",
    "total_sqft",
    "bath",
    "balcony",
    "latitude",
    "longitude",
    "distance_school_km",
    "distance_hospital_km",
    "distance_college_km",
    "distance_bus_stop_km",
    "distance_railway_station_km",
    "distance_shopping_km",
    "distance_bank_km",
    "distance_park_km"
]


preprocessor = ColumnTransformer(
    transformers=[
        (
            "cat",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categorical_features
        ),
        (
            "num",
            "passthrough",
            numeric_features
        )
    ]
)


# ============================================================
# 9. MODELS
# ============================================================

models = {

    "Linear Regression":
        LinearRegression(),

    "Random Forest":
        RandomForestRegressor(
            n_estimators=150,
            random_state=42,
            n_jobs=-1
        ),

    "Gradient Boosting":
        GradientBoostingRegressor(
            n_estimators=150,
            learning_rate=0.05,
            max_depth=3,
            random_state=42
        ),

    "XGBoost":
        XGBRegressor(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="reg:squarederror",
            random_state=42,
            n_jobs=-1
        )
}


# ============================================================
# 10. TRAIN + EVALUATE
# ============================================================

results = []

print("\n===================================")
print("TRAINING MODELS")
print("===================================")


for name, model in models.items():

    print(f"\nTraining {name}...")

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model)
        ]
    )

    pipeline.fit(
        X_train,
        y_train
    )

    predictions = pipeline.predict(X_test)

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    mse = mean_squared_error(
        y_test,
        predictions
    )

    rmse = np.sqrt(mse)

    r2 = r2_score(
        y_test,
        predictions
    )

    results.append({
        "Model": name,
        "MAE": mae,
        "MSE": mse,
        "RMSE": rmse,
        "R2": r2
    })

    print(
        f"MAE  : {mae:.4f}"
    )

    print(
        f"MSE  : {mse:.4f}"
    )

    print(
        f"RMSE : {rmse:.4f}"
    )

    print(
        f"R2   : {r2:.4f}"
    )

    # Save model
    filename = (
        name.lower()
        .replace(" ", "_")
        + ".pkl"
    )

    joblib.dump(
        pipeline,
        f"models/{filename}"
    )


# ============================================================
# 11. SAVE RESULTS
# ============================================================

results_df = pd.DataFrame(results)

results_df.to_csv(
    RESULT_FILE,
    index=False
)

print("\n===================================")
print("MODEL COMPARISON")
print("===================================")

print(
    results_df.to_string(
        index=False
    )
)

print("\nSaved:", RESULT_FILE)

print("\nDONE.")