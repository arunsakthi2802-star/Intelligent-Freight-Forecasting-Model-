import pandas as pd
import numpy as np
import joblib
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import os

from .logger import get_logger

logger = get_logger("vessel_eta")

def train_eta_model(data_path="d:/FREIGHT MODEL/freight data set/vessel dataset/processed_AIS_dataset.csv"):
    logger.info(f"Loading AIS dataset from {data_path}...")
    
    # Read a sample if it's too large for quick local training, but we'll try reading all
    try:
        df = pd.read_csv(data_path, nrows=500000) # Load up to 500k rows for efficiency
    except FileNotFoundError:
        logger.error(f"File not found: {data_path}")
        return
        
    logger.info(f"Loaded {len(df)} rows. Processing features...")
    
    # Target: ETA_hours
    target = 'ETA_hours'
    
    if target not in df.columns:
        logger.error(f"Target '{target}' not found in the dataset.")
        return
        
    # Drop rows with missing target
    df = df.dropna(subset=[target])
    
    # Select features useful for ETA prediction
    features = [
        'LAT', 'LON', 'SOG_kmh', 'dist_km', 'Length', 'Width', 'Draft', 
        'VesselType_enc', 'Cargo_enc', 'Status_enc', 'dest_lat', 'dest_lon'
    ]
    
    # Ensure all features exist
    features = [f for f in features if f in df.columns]
    
    X = df[features]
    y = df[target]
    
    logger.info("Splitting dataset into train and test sets...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Preprocessing
    preprocessor = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    logger.info("Fitting preprocessor...")
    X_train_prep = preprocessor.fit_transform(X_train)
    X_test_prep = preprocessor.transform(X_test)
    
    os.makedirs('models', exist_ok=True)
    joblib.dump(preprocessor, 'models/ais_preprocessor.joblib')
    
    models = {
        'XGBoost': XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1),
        'LightGBM': LGBMRegressor(n_estimators=200, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1)
    }
    
    best_name = None
    best_model = None
    best_mae = float('inf')
    
    for name, model in models.items():
        logger.info(f"Training {name} for ETA Prediction...")
        model.fit(X_train_prep, y_train)
        
        preds = model.predict(X_test_prep)
        mae = mean_absolute_error(y_test, preds)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        r2 = r2_score(y_test, preds)
        
        logger.info(f"{name} Performance -> MAE: {mae:.2f} hours | RMSE: {rmse:.2f} | R2: {r2:.4f}")
        
        if mae < best_mae:
            best_mae = mae
            best_model = model
            best_name = name
            
    logger.info(f"Selected {best_name} as final ETA model (Best MAE: {best_mae:.2f} hours)")
    
    joblib.dump(best_model, 'models/vessel_eta_model.joblib')
    
    # Feature importance
    if hasattr(best_model, 'feature_importances_'):
        importances = best_model.feature_importances_
        fi_df = pd.DataFrame({'feature': features, 'importance': importances})
        fi_df = fi_df.sort_values('importance', ascending=False)
        fi_df.to_csv('reports/ais_feature_importance.csv', index=False)
        logger.info("Saved feature importance to reports/ais_feature_importance.csv")
        
    logger.info("Vessel ETA Training pipeline completed successfully.")
    
if __name__ == "__main__":
    train_eta_model()
