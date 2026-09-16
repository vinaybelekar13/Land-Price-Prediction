import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

df = pd.read_csv("data/final_gis_dataset.csv")

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
y = df["price"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

# ---------------------------------------------------------
# Model comparison graph
# ---------------------------------------------------------

results = pd.read_csv("results/model_comparison.csv")

plt.figure(figsize=(10, 6))

plt.bar(results["Model"], results["R2"])

plt.ylabel("R² Score")
plt.xlabel("Model")
plt.title("Model Comparison - R² Score")

plt.xticks(rotation=15)

plt.tight_layout()

plt.savefig(
    "results/model_r2_comparison.png",
    dpi=300
)

plt.close()


# ---------------------------------------------------------
# RMSE graph
# ---------------------------------------------------------

plt.figure(figsize=(10, 6))

plt.bar(results["Model"], results["RMSE"])

plt.ylabel("RMSE")
plt.xlabel("Model")
plt.title("Model Comparison - RMSE")

plt.xticks(rotation=15)

plt.tight_layout()

plt.savefig(
    "results/model_rmse_comparison.png",
    dpi=300
)

plt.close()


# ---------------------------------------------------------
# XGBoost actual vs predicted
# ---------------------------------------------------------

model = joblib.load(
    "models/xgboost.pkl"
)

predictions = model.predict(X_test)

plt.figure(figsize=(8, 6))

plt.scatter(
    y_test,
    predictions,
    alpha=0.5
)

minimum = min(
    y_test.min(),
    predictions.min()
)

maximum = max(
    y_test.max(),
    predictions.max()
)

plt.plot(
    [minimum, maximum],
    [minimum, maximum]
)

plt.xlabel("Actual Price (Lakhs)")
plt.ylabel("Predicted Price (Lakhs)")
plt.title("XGBoost - Actual vs Predicted Prices")

plt.tight_layout()

plt.savefig(
    "results/xgboost_actual_vs_predicted.png",
    dpi=300
)

plt.close()


# ---------------------------------------------------------
# Sample predictions
# ---------------------------------------------------------

sample = X_test.head(10).copy()

sample_predictions = model.predict(sample)

sample_output = sample.copy()

sample_output["Actual_Price_Lakhs"] = y_test.loc[
    sample.index
].values

sample_output["Predicted_Price_Lakhs"] = sample_predictions

sample_output.to_csv(
    "results/sample_predictions.csv",
    index=False
)


print("\n===================================")
print("RESULTS FILES GENERATED")
print("===================================")

print("\nCreated:")

print("results/model_r2_comparison.png")
print("results/model_rmse_comparison.png")
print("results/xgboost_actual_vs_predicted.png")
print("results/sample_predictions.csv")

print("\nSample predictions:")
print(
    sample_output[
        [
            "location",
            "bhk",
            "total_sqft",
            "Actual_Price_Lakhs",
            "Predicted_Price_Lakhs"
        ]
    ].to_string(index=False)
)

print("\nDONE.")