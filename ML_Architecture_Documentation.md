# SIH26006: AI Engine & Machine Learning Architecture Documentation

This document outlines the complete Machine Learning (ML) architecture, algorithms, and logic systems built for the **Ocean Freight Forecasting & Logistics Optimization Engine**. 

## 1. System Architecture Overview

The system is designed as a multi-tier AI Decision Engine bridging predictive forecasting with actionable operational logistics:

1. **Predictive Tier (Forecasting)**
   * **Freight Rate Forecasting:** Predicts future ocean freight pricing (USD/Container) based on historical trade, oil prices, and port capacity.
   * **Vessel ETA Forecasting:** Predicts the remaining hours to destination for ships mid-voyage based on AIS tracking data.
2. **Operations Tier (Routing & Cost)**
   * **Voyage Cost Optimizer:** Calculates the physical shortest route and estimates fuel/charter costs across various speed profiles.
3. **Planning Tier (Logistics)**
   * **Logistics Planner:** Assigns fleets of vessels to predicted profitable routes to maximize overall network operating profit.
4. **Real-Time Integration Tier**
   * **Live Tracking Engine:** Actively monitors a specific voyage, pulling live OpenWeather and NewsData.io feeds while recalculating route trajectories.

---

## 2. ML Algorithms & Implementations

### A. Freight Rate Forecasting Model
* **Objective:** Predict the exact freight rate in USD for a specific maritime route.
* **Algorithm Selection:** The pipeline dynamically tests multiple regression algorithms and selects the best performer. The primary algorithms utilized are:
  1. **RandomForest Regressor (Best Performer - 99.33% R²)**: An ensemble method utilizing decision trees. Highly robust against overfitting and capable of handling non-linear relationships in trade and oil indices.
  2. **XGBoost (Extreme Gradient Boosting)**: Heavily utilized for its speed and regularization.
  3. **LightGBM & CatBoost**: Secondary gradient boosting frameworks used for rapid evaluation of categorical port data.
* **Feature Engineering:**
  * **Time-Series Lags:** Features include rolling averages and historical lags to capture market momentum.
  * **Leakage Prevention:** Automated Pearson correlation checks drop features exceeding `0.95` correlation to prevent the model from memorizing the target.

### B. Vessel ETA Predictor
* **Objective:** Predict the remaining duration of a voyage (ETA Hours) using live AIS coordinates and vessel parameters.
* **Algorithm Selection:** **XGBoost Regressor (99.98% R²)**
* **Key Features:** Latitude (`LAT`), Longitude (`LON`), Speed Over Ground (`SOG_kmh`), Distance to destination (`dist_km`), and Vessel Draft/Capacity.
* **Why XGBoost?:** Spatial and kinematic data (speed, distance) contain highly complex interactions that Gradient Boosting handles exceptionally well, achieving an error margin of under 6 minutes.

### C. Route & Voyage Optimizer
* **Objective:** Determine the shortest physical maritime route and lowest-cost speed profile.
* **Algorithm Selection:** **Dijkstra’s Shortest Path Algorithm** (via `networkx`)
* **Mechanism:** 
  * A virtual graph of global maritime waypoints (e.g., Suez Canal, Singapore Strait) is constructed.
  * Dijkstra's algorithm guarantees the mathematical absolute shortest distance between the Origin and Destination ports.
  * A deterministic **Cost Function** calculates fuel burn `(capacity * speed^2)` and charter rates to output the total USD cost for "Eco Slow", "Standard", and "Fast" speed profiles.

### D. Logistics Fleet Optimization
* **Objective:** Assign a limited fleet of vessels to multiple routes to maximize total network profit.
* **Algorithm Selection:** **Constraint Programming (CP-SAT)** via Google OR-Tools.
* **Mechanism:** 
  * The model takes the predicted freight rates (from the ML model) and the operating costs (from the Voyage model).
  * It applies constraints: *A vessel can only sail one route at a time; A route needs at least one vessel.*
  * The solver navigates the combinatorial space to find the configuration that maximizes `Total Profit = (Freight Rate * Capacity) - Operating Cost`.

---

## 3. Data Processing Pipeline

1. **Imputation:** Missing data in the port and trade datasets are handled using `SimpleImputer` (median strategy).
2. **Scaling:** Continuous variables (like oil prices and distances) are normalized using `StandardScaler` to ensure Gradient Boosting models converge quickly without bias.
3. **Validation Strategy:** Chronological splitting (Train: 70%, Validation: 15%, Test: 15%) is strictly enforced to prevent predicting the past using future data.

## 4. Live Tracking & Data Feeds
The `live_engine.py` script bridges the ML models with real-world APIs:
* **OpenWeather API:** Pulled via standard REST HTTP requests every 30 seconds for live environmental hazard monitoring.
* **NewsData.io API:** NLP queries filter for global maritime disruption news (e.g., canal blockages, piracy) to factor into route risk multipliers.
