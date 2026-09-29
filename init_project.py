import os

dirs = [
    "data/raw/freight", "data/raw/trade", "data/raw/economic", "data/raw/fuel", 
    "data/raw/weather", "data/raw/ports", "data/raw/vessels", "data/raw/ais", 
    "data/raw/news", "data/raw/companies", "data/cleaned", "data/merged", 
    "data/features", "data/training", "data/predictions", "data/tracking", 
    "data/routes", "data/reference", "data/demo",
    "models/forecasting", "models/demand", "models/risk", "models/anomaly", 
    "models/nlp", "models/vessel", "models/eta", "models/cost", "models/preprocessing",
    "reports/data_quality", "reports/forecasting", "reports/backtesting", 
    "reports/vessel", "reports/route", "reports/weather", "reports/cost", 
    "reports/risk", "reports/news", "reports/tracking", "reports/decision",
    "map/data",
    "src/ingestion", "src/preprocessing", "src/features", "src/forecasting", 
    "src/demand", "src/anomaly", "src/nlp", "src/ais", "src/weather", 
    "src/optimization", "src/risk", "src/cost", "src/decision", "src/utils",
    "tests"
]

for d in dirs:
    os.makedirs(f"sih26006_ai/{d}", exist_ok=True)

# Create some basic files
open("sih26006_ai/.env.example", "w").write("MARINETRAFFIC_API_KEY=\nAISHUB_USERNAME=\n")
open("sih26006_ai/README.md", "w").write("# SIH26006 AI SYSTEM\n")

# Create __init__.py files in src and subdirectories
src_dirs = [d for d in dirs if d.startswith("src/")] + ["src"]
for d in src_dirs:
    open(f"sih26006_ai/{d}/__init__.py", "w").close()

print("Directory structure created.")
