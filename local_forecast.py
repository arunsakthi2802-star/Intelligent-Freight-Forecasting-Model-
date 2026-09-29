import pandas as pd
import joblib
import argparse
import os
import warnings
warnings.filterwarnings('ignore')

from pipeline.logger import get_logger
logger = get_logger("local_forecast")

def predict_freight(input_file):
    logger.info(f"Loading freight input data from {input_file}...")
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        logger.error(f"Could not find input file: {input_file}")
        return
        
    from pipeline.feature_engineering import create_time_features
    
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df = create_time_features(df)
        if 'origin_port' in df.columns and 'destination_port' in df.columns:
            df['route'] = df['origin_port'] + "_" + df['destination_port']
            
    logger.info("Loading Freight Preprocessor and Model...")
    preprocessor = joblib.load('models/preprocessor.joblib')
    model = joblib.load('models/freight_model.joblib')
    
    # Ensure all features exist
    expected_numeric = preprocessor.transformers_[0][2]
    expected_categorical = preprocessor.transformers_[1][2]
    
    for col in expected_numeric:
        if col not in df.columns: df[col] = 0
    for col in expected_categorical:
        if col not in df.columns: df[col] = 'Unknown'
            
    X_pred = df[expected_numeric + expected_categorical]
    
    logger.info("Transforming data & Predicting Freight Rate (USD)...")
    X_pred_prep = preprocessor.transform(X_pred)
    preds = model.predict(X_pred_prep)
    
    df['predicted_freight_rate_usd'] = preds
    
    out_cols = ['date', 'origin_port', 'destination_port', 'container_type', 'predicted_freight_rate_usd']
    out_cols = [c for c in out_cols if c in df.columns]
    
    os.makedirs('predictions', exist_ok=True)
    out_path = 'predictions/freight_predictions.csv'
    df[out_cols].to_csv(out_path, index=False)
    logger.info(f"Freight Rate Predictions successfully saved to {out_path}")


def predict_eta(input_file):
    logger.info(f"Loading AIS input data from {input_file}...")
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        logger.error(f"Could not find input file: {input_file}")
        return
        
    logger.info("Loading AIS Preprocessor and Model...")
    try:
        preprocessor = joblib.load('models/ais_preprocessor.joblib')
        model = joblib.load('models/vessel_eta_model.joblib')
    except Exception as e:
        logger.error(f"Could not load models: {e}. Run 'python run.py train_ais' first.")
        return
        
    features = [
        'LAT', 'LON', 'SOG_kmh', 'dist_km', 'Length', 'Width', 'Draft', 
        'VesselType_enc', 'Cargo_enc', 'Status_enc', 'dest_lat', 'dest_lon'
    ]
    
    # Fill missing features with 0 for demo purposes
    for f in features:
        if f not in df.columns:
            df[f] = 0.0
            
    X_pred = df[features]
    
    logger.info("Transforming data & Predicting ETA (Hours)...")
    X_pred_prep = preprocessor.transform(X_pred)
    preds = model.predict(X_pred_prep)
    
    df['predicted_ETA_hours'] = preds
    
    out_cols = ['MMSI', 'VesselName', 'LAT', 'LON', 'dest_lat', 'dest_lon', 'predicted_ETA_hours']
    out_cols = [c for c in out_cols if c in df.columns]
    
    os.makedirs('predictions', exist_ok=True)
    out_path = 'predictions/vessel_eta_predictions.csv'
    df[out_cols].to_csv(out_path, index=False)
    logger.info(f"Vessel ETA Predictions successfully saved to {out_path}")

def interactive_predict():
    print("\n--- 🚢 INTERACTIVE FREIGHT PREDICTION ---")
    date_val = input("Enter Date (YYYY-MM-DD) [e.g. 2024-12-01]: ") or "2024-12-01"
    origin = input("Enter Origin Port [e.g. INMAA]: ") or "INMAA"
    dest = input("Enter Destination Port [e.g. AEDXB]: ") or "AEDXB"
    oil = input("Enter current Oil Price (USD) [e.g. 80.0]: ") or "80.0"
    
    # Generate temporary prediction file
    data = [{
        'date': date_val,
        'origin_port': origin,
        'destination_port': dest,
        'container_type': '20ft',
        'oil_price': float(oil),
        'port_throughput_teu': 150000
    }]
    
    temp_file = 'data/sample/interactive_input.csv'
    pd.DataFrame(data).to_csv(temp_file, index=False)
    
    print("\nProcessing prediction...\n")
    predict_freight(temp_file)
    
    # Read and show the result nicely
    res = pd.read_csv('predictions/freight_predictions.csv')
    predicted_rate = res['predicted_freight_rate_usd'].iloc[-1]
    
    print(f"\n✅ PREDICTION RESULT: The predicted freight rate for {origin} -> {dest} is ${predicted_rate:,.2f} USD\n")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Local Forecast & Prediction Tool for SIH26006")
    subparsers = parser.add_subparsers(dest="command", help="Prediction task to run")
    
    parser_freight = subparsers.add_parser('freight', help="Predict Freight Rate")
    parser_freight.add_argument('--input', type=str, required=True, help="Input CSV file for freight prediction")
    
    parser_eta = subparsers.add_parser('eta', help="Predict Vessel ETA from AIS data")
    parser_eta.add_argument('--input', type=str, required=True, help="Input CSV file for vessel ETA prediction")
    
    parser_plan = subparsers.add_parser('plan', help="Run logistics optimization based on freight predictions")
    parser_interactive = subparsers.add_parser('interactive', help="Interactively ask for data in terminal and predict")
    
    parser_voyage = subparsers.add_parser('voyage', help="Predict shortest route and lowest cost for a voyage")
    parser_voyage.add_argument('--origin', type=str, required=True, help="Origin port code")
    parser_voyage.add_argument('--destination', type=str, required=True, help="Destination port code")
    parser_voyage.add_argument('--capacity', type=int, default=10000, help="Vessel capacity in TEU")
    parser_voyage.add_argument('--fuel_price', type=float, default=600.0, help="Fuel price per ton in USD")
    
    args = parser.parse_args()
    
    if args.command == 'freight':
        predict_freight(args.input)
    elif args.command == 'eta':
        predict_eta(args.input)
    elif args.command == 'interactive':
        interactive_predict()
    elif args.command == 'plan':
        from pipeline.logistics_optimization import run_logistics_pipeline
        run_logistics_pipeline()
    elif args.command == 'voyage':
        from pipeline.voyage_cost_optimizer import predict_lowest_cost_route
        predict_lowest_cost_route(args.origin, args.destination, args.capacity, args.fuel_price)
    else:
        parser.print_help()
