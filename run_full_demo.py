import os
import json
import pandas as pd
from src.schemas import VoyageRequest
from src.services import process_voyage_request
from pipeline.logger import get_logger

logger = get_logger()

def run_demo():
    logger.info("Starting COMPLETE DEMO WORKFLOW for SIH26006")
    logger.info("DATA -> CLEAN -> FEATURES -> FORECAST -> VESSEL AVAILABILITY ... -> FINAL DECISION")
    
    # 1. Setup Data & Directories
    os.makedirs("reports/decision", exist_ok=True)
    os.makedirs("reports/optimization", exist_ok=True)
    
    # 2. Simulate User Request (75,000 tonnes Coal to Paradip)
    req = VoyageRequest(
        cargo_type="COAL",
        cargo_quantity_tonnes=75000,
        origin_country="AUSTRALIA",
        loading_port="OPTIONAL",
        destination_port="PARADIP",
        loading_date="2024-11-15",
        latest_arrival_date="2024-12-10",
        vessel_classes=["PANAMAX", "CAPESIZE"]
    )
    
    logger.info(f"Processing Request for {req.cargo_quantity_tonnes}T {req.cargo_type} to {req.destination_port}")
    
    # 3. Process Voyage
    result = process_voyage_request(req)
    
    logger.info("VESSEL CANDIDATES DISCOVERED")
    logger.info("WEATHER IMPACT PREDICTED")
    logger.info("ROUTES OPTIMIZED")
    logger.info("COSTS & RISK CALCULATED")
    
    # 4. Generate Reports
    with open("reports/decision/voyage_plan.json", "w") as f:
        json.dump(result, f, indent=4)
        
    # Generate CSV
    df = pd.DataFrame(result['candidate_vessels'])
    df.to_csv("reports/optimization/low_cost_vessels.csv", index=False)
    df.to_csv("reports/decision/voyage_plan.csv", index=False)
    
    # Generate TXT
    with open("reports/decision/voyage_plan.txt", "w") as f:
        f.write("============================================================\n")
        f.write("VOYAGE PLAN REPORT\n")
        f.write("============================================================\n")
        f.write(f"CARGO: {req.cargo_quantity_tonnes} tonnes of {req.cargo_type}\n")
        f.write(f"ORIGIN: {req.origin_country}\n")
        f.write(f"DESTINATION: {req.destination_port}\n")
        f.write(f"LOADING DATE: {req.loading_date}\n\n")
        f.write("TOP VESSEL CANDIDATES:\n")
        for v in result['candidate_vessels']:
            f.write(f"- {v['name']} ({v['vessel_class']}) | Status: {v['availability_status']} ({v['availability_probability']}) | Cost: ${v['predicted_total_cost']}\n")
        
        f.write("\nLOGISTICS TIMES:\n")
        f.write(f"- Loading: {result['loading_forecast']['expected_hours']}h\n")
        f.write(f"- Unloading: {result['unloading_forecast']['expected_hours']}h\n")
        
    logger.info("Generated reports in reports/decision/")
    logger.info("COMPLETE DEMO WORKFLOW EXECUTED SUCCESSFULLY")

if __name__ == "__main__":
    run_demo()
