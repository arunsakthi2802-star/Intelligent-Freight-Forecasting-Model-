import pandas as pd
import joblib
import argparse
import os

def predict(input_file):
    print(f"Loading data from {input_file}...")
    df = pd.read_csv(input_file)
    
    # We might need to engineer some basic features if the prediction dataset is raw.
    # For a real pipeline, the predict script should apply the feature engineering logic, 
    # but based on the prompt's simplicity we assume prediction_input.csv has matching features
    # to the preprocessor except the engineered ones, so let's import feature engineering.
    from pipeline.feature_engineering import create_time_features
    
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df = create_time_features(df)
        if 'origin_port' in df.columns and 'destination_port' in df.columns:
            df['route'] = df['origin_port'] + "_" + df['destination_port']
            
    print("Loading preprocessor and model...")
    preprocessor = joblib.load('models/preprocessor.joblib')
    model = joblib.load('models/freight_model.joblib')
    
    # Ensure all features expected by preprocessor are present (fill with 0 or unknown if missing for demo)
    expected_numeric = preprocessor.transformers_[0][2]
    expected_categorical = preprocessor.transformers_[1][2]
    
    for col in expected_numeric:
        if col not in df.columns:
            df[col] = 0
            
    for col in expected_categorical:
        if col not in df.columns:
            df[col] = 'Unknown'
            
    X_pred = df[expected_numeric + expected_categorical]
    
    print("Transforming data...")
    X_pred_prep = preprocessor.transform(X_pred)
    
    print("Predicting...")
    preds = model.predict(X_pred_prep)
    
    # Add predictions to original
    df['predicted_freight_rate_usd'] = preds
    
    # Select final columns to output
    out_cols = ['date', 'origin_port', 'destination_port', 'container_type', 'predicted_freight_rate_usd']
    out_cols = [c for c in out_cols if c in df.columns]
    
    os.makedirs('predictions', exist_ok=True)
    out_path = 'predictions/prediction_results.csv'
    df[out_cols].to_csv(out_path, index=False)
    
    print(f"Predictions saved to {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True, help='Input CSV for prediction')
    args = parser.parse_args()
    predict(args.input)
