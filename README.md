@"
# Land Price Prediction System Using Nearby Amenities

## 📌 Project Overview

This project develops a Machine Learning based land/property price prediction system for Bengaluru by incorporating both property characteristics and nearby amenities.

Traditional property price prediction models mainly depend on factors such as area, number of bedrooms and bathrooms. This project extends the prediction process by incorporating spatial information and distances to nearby amenities such as schools, hospitals, colleges, bus stops, railway stations, shopping centres, banks and parks.

The system combines:

- Property data
- Geographic location
- Nearby amenity information
- Distance-based feature engineering
- Machine Learning models
- Interactive web-based prediction

---

## 🎯 Objectives

### Main Objective

To develop a Machine Learning based price prediction system that considers nearby amenities and geographic factors along with property characteristics.

### Sub-objectives

1. Collect and preprocess Bengaluru property price data.
2. Clean missing, duplicate and inconsistent records.
3. Obtain geographic coordinates for property localities.
4. Collect nearby amenity information using OpenStreetMap-based spatial data.
5. Generate distance-based features for important amenities.
6. Train and compare multiple Machine Learning regression models.
7. Evaluate models using MAE, MSE, RMSE and R².
8. Develop a web application for price prediction and spatial visualization.

---

## 🗂️ Dataset

The primary property dataset is the:

**Bangalore Housing Prices dataset by Aryan Felix**

The dataset contains property-related attributes including:

- Area Type
- Availability
- Location
- Size
- Society
- Total Sq. Ft
- Bath
- Balcony
- Price

The project uses Bengaluru as the study area.

> Note: The source dataset contains residential property prices rather than direct land-transaction prices. Therefore, the project uses the dataset as a proxy for location-sensitive real-estate valuation.

---

## 🗺️ GIS and Amenity Features

Locality-level geographic coordinates are obtained through geocoding.

Nearby amenities are incorporated as spatial features.

The project considers distances to categories such as:

- Schools
- Hospitals
- Colleges / Universities
- Bus Stops
- Railway Stations
- Shopping Centres / Supermarkets
- Banks / ATMs
- Parks

These geographic features are combined with property attributes before Machine Learning model training.

---

## ⚙️ Methodology

```text
Property Dataset
       ↓
Data Cleaning
       ↓
Outlier Detection & Removal
       ↓
Locality Geocoding
       ↓
Coordinate Validation
       ↓
Nearby Amenity Collection
       ↓
Distance Feature Engineering
       ↓
Final GIS Dataset
       ↓
Train-Test Split
       ↓
Machine Learning Models
       ↓
Model Evaluation
       ↓
Best Performing Model
       ↓
Price Prediction
       ↓
Web Application
