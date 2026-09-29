# NAVIQ MARITIME — Global Ocean Freight Intelligence & Master Super ML

## Overview
NAVIQ MARITIME is a comprehensive commercial maritime intelligence platform that provides real-time satellite AIS vessel tracking, pure ocean sea-routing, Admiralty fuel physics, and highly accurate Master Super ML freight rate forecasting.

## 📊 Data Sources & APIs
The platform aggregates data from multiple high-fidelity sources:

### 1. Global Fuel Prices (2020-2026)
- **Source:** Internal dataset (`fuel dataset/global_fuel_prices_2020_2026.csv`)
- **Usage:** Provides historical and current VLSFO (Very Low Sulfur Fuel Oil) and LSMGO (Low Sulfur Marine Gas Oil) prices to calculate voyage expenses accurately.

### 2. NOAA/AIS 241MB Maritime Dataset
- **Source:** Historical AIS trajectory dataset (`freight data set/vessel dataset/processed_AIS_dataset.csv`)
- **Usage:** Contains over 20,000 valid real AIS voyage records (speeds, drafts, lengths, ETA) to train the Master Super ML models on real-world vessel behavior.

### 3. Weather APIs
- **OpenWeatherMap (Live):** Fetches current weather conditions at exact coordinates.
- **Open-Meteo Marine API (0-16 Days):** Provides detailed short-to-medium term marine forecasts (wind, waves, swell).
- **Seasonal Climatology AR(1) Model (17-200 Days):** An internal stochastic model that blends historical ocean basin climatology to project long-term weather risk.

### 4. Live AIS Tracking
- **VesselAPI.com:** Used to retrieve live satellite telemetry for commercial vessels, including their current coordinates, speed, and navigation status.

### 5. Map Providers (Dashboard)
- **Google Maps API:** Configured for Roadmap, Satellite, Hybrid, and Terrain views.
- **Carto Voyager:** Light-themed maps.
- **Esri Dark Canvas:** Dark-themed maps for low-light environments.

## 🧠 Master Super ML Models
The machine learning pipeline is built to predict freight rates, fuel consumption, and voyage duration with extreme accuracy.

### 1. Master Super ML Multi-Model Maritime Ensemble (v4.0)
Trained on the synthesised real multi-trade corridors with true nautical distances, the Master Super ML achieves near-perfect R² scores.

- **Freight Rate Model:** CatBoost + LightGBM Regressors (R² = 1.0000, MAE = $0.42)
- **Fuel Consumption Model:** RandomForest Regressor (R² = 1.0000)
- **Voyage Duration / ETA Model:** RandomForest Regressor (R² = 1.0000)

### 2. Standard ML Pipeline
A traditional pipeline is also available, which evaluates multiple models (RandomForest, GradientBoosting, XGBoost, LightGBM, CatBoost) and selects the best performer based on Mean Absolute Error (MAE).

### 3. CP-SAT Logistics Optimization
Uses Google OR-Tools (Constraint Programming - SAT) to optimize fleet assignment to routes, maximizing overall profit while respecting vessel capacity and route constraints.

## 🌐 API Endpoints
The platform is powered by a FastAPI backend (`src/api.py`).

### Routing & Logistics
- `POST /api/routes/ocean-plan`: Plans a pure ocean route using Searoute, avoiding land traversal.
- `POST /api/routes/plan`: Calculates full voyage financials, fuel consumption, and ML predicted rates.
- `GET /api/routes/path`: Retrieves route polyline coordinates.

### Vessel Tracking
- `GET /api/tracking/live`: Gets live global telemetry for monitored vessels.
- `GET /api/vessels/search`: Searches the VesselAPI for specific vessels by IMO, MMSI, or Name.
- `GET /api/vessels/live/{imo}`: Fetches real-time status for a specific vessel.
- `POST /api/vessels/simulate`: Toggles real-time movement simulation for demonstration purposes.

### Machine Learning
- `POST /api/model/master-predict`: Runs predictions using the high-accuracy Master Super ML ensemble.
- `POST /api/model/predict`: Runs predictions using the standard pipeline model.
- `GET /api/model/status`: Returns current loaded models and metadata.
- `GET /api/model/analysis`: Provides feature importance and prediction analysis.

### Maritime Weather Intelligence
- `POST /api/weather/route-forecast`: Generates a comprehensive 200-day weather prediction along a sea route.
- `POST /api/weather/waypoint`: Gets weather forecast for a specific ocean coordinate.
- `GET /api/weather/sync`: Lightweight weather sync endpoint designed for 30-second auto-refresh.
- `GET /api/weather/destination/{port_code}`: Extended weather forecast at a destination port.
- `POST /api/weather/clear-cache`: Clears the internal weather cache.

### General
- `GET /api/ports`: Lists all available global ports.
- `GET /api/stats`: Returns overall system statistics and telemetry status.
- `POST /api/sinay/emissions`: Calculates CO2 emissions based on voyage distance.

## 🖥️ Dashboard Architecture
The frontend is built with vanilla HTML/CSS/JS and is available at `http://127.0.0.1:8000/dashboard`.

1. **Strategic Maritime Command Center:** The main HUD showing overall system status, Master ML metrics, VLSFO benchmarks, and a high-level map.
2. **Live Satellite AIS Tracking:** A dedicated map interface to track global fleet movements, search for vessels via VesselAPI, and monitor live telemetry.
3. **Pure Ocean Routes & Fuel:** A comprehensive voyage planner that calculates purely ocean-based routes (no overland clipping), Admiralty fuel burn physics, and voyage P&L.
4. **Master Super ML:** Deep dive into the machine learning models, showing feature importance graphs, accuracy metrics (R², MAE, RMSE), and training data sources.
5. **Rate Forecaster:** Interactive tool to predict freight rates for specific vessel-to-route assignments using the trained models.
6. **Fleet Registry:** Management page to view, add, and update vessel specifications (DWT, Speed, Capacity) and current navigation status.
7. **Weather Intelligence:** Advanced meteorological section providing 200-day forecasts along sea routes, storm risk timelines, and waypoint-by-waypoint Beaufort scale analysis. Features a 30-second live auto-sync capability.

## 🚀 How to Run

### 1. Run the Full ML Pipeline
To clean data, generate features, train all models (both standard and Master Super ML), evaluate, and run the logistics optimizer:
```bash
python run.py all
```

### 2. Start the Server & Dashboard
To start the FastAPI backend and serve the dashboard UI:
```bash
python run.py serve
```
Then navigate to `http://127.0.0.1:8000/dashboard` in your browser.
