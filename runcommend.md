# NAVIQ Maritime - Commands and Resources

## 1. The "Run All" Command (Recommended)
We have created a single script that trains all Master Super ML models (on live real data) and immediately starts the Fast API server right after. 

**Run this single command:**
```bat
run_all.bat
```
*(This will automatically train the ML pipeline and start the server so it doesn't crash from missing modules).*

---

## 2. Individual Commands (Optional)

If you prefer to run them separately:

**Train the Super Master ML Model:**
```bat
python src/train_master_super_ml.py
```

**Start the Backend API & Server:**
```bat
python -m src.api
```
*(Note: We use `-m src.api` to ensure Python correctly resolves the `src` module structure without raising `ModuleNotFoundError`.)*

---

## 3. URLs and Resources

Once the server is running, you can access the dashboard and APIs via these links:

- **Web Dashboard URL:** [http://127.0.0.1:8000/dashboard](http://127.0.0.1:8000/dashboard)
- **Standalone Vessel Calculator:** [http://127.0.0.1:8000/dashboard/freightvessel](http://127.0.0.1:8000/dashboard/freightvessel)
- **API Documentation (Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Integrated APIs:
- **CARTO Basemap API Key:** `cb1_422s_1_18d3c5129f1ec78f35876c58` (Used for dynamic routing and real-time fleet radar without watermarks).
- **Google Maps API Key:** `AIzaSyBcKZ18GLlGVS_72a96SAEH2oaS1kOH_XM` (Used for satellite and terrain roadmap options).
