import pandas as pd
import numpy as np
import joblib
from datetime import datetime
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import json

from .logger import get_logger

logger = get_logger()

def create_preprocessor(numeric_features, categorical_features):
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median'))
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])
    return preprocessor

def train_pipeline():
    logger.info("Starting TRAIN pipeline")
    
    train = pd.read_csv('data/training/train.csv')
    val = pd.read_csv('data/training/val.csv')
    
    target = 'target_next_week'
    drop_cols = ['date', 'route', 'target_next_week', 'freight_rate_usd']
    # Wait, freight_rate_usd should be allowed? Yes, it's the current week's price, it predicts next week.
    # Let's just drop date, route, target_next_week
    features = [c for c in train.columns if c not in ['date', 'route', 'target_next_week']]
    
    X_train = train[features]
    y_train = train[target]
    
    X_val = val[features]
    y_val = val[target]
    
    numeric_features = X_train.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_features = X_train.select_dtypes(include=['object', 'category']).columns.tolist()
    
    logger.info(f"Numeric features: {len(numeric_features)}")
    logger.info(f"Categorical features: {len(categorical_features)}")
    
    preprocessor = create_preprocessor(numeric_features, categorical_features)
    
    # Fit preprocessor strictly on training data
    logger.info("Fitting preprocessor on training data...")
    X_train_prep = preprocessor.fit_transform(X_train)
    X_val_prep = preprocessor.transform(X_val)
    
    joblib.dump(preprocessor, 'models/preprocessor.joblib')
    
    # Train models
    models = {
        'RandomForest': RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1),
        'GradientBoosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
        'XGBoost': XGBRegressor(n_estimators=300, random_state=42, n_jobs=-1),
        'LightGBM': LGBMRegressor(n_estimators=300, random_state=42, n_jobs=-1, verbose=-1, min_child_samples=5),
        'CatBoost': CatBoostRegressor(iterations=300, random_seed=42, verbose=0)
    }
    
    best_name = None
    best_model = None
    best_mae = float('inf')
    
    for name, model in models.items():
        logger.info(f"Training {name}...")
        model.fit(X_train_prep, y_train)
        preds = model.predict(X_val_prep)
        mae = mean_absolute_error(y_val, preds)
        logger.info(f"{name} MAE: {mae:.2f}")
        
        if mae < best_mae:
            best_mae = mae
            best_model = model
            best_name = name
    
    logger.info(f"Selecting {best_name} as final model based on validation MAE (Best MAE: {best_mae:.2f})")
    
    joblib.dump(best_model, 'models/freight_model.joblib')
    
    # Feature importance extraction
    if hasattr(best_model, 'feature_importances_'):
        try:
            feature_names = preprocessor.get_feature_names_out()
            importances = best_model.feature_importances_
            fi_df = pd.DataFrame({'feature': feature_names, 'importance': importances})
            fi_df = fi_df.sort_values('importance', ascending=False)
            fi_df.to_csv('reports/feature_importance.csv', index=False)
            fi_df.head(20).to_csv('reports/top_features.csv', index=False)
        except Exception as e:
            logger.warning(f"Could not extract feature importance: {e}")
            
    # Model Metadata
    metadata = {
        'model_name': best_name,
        'training_date': datetime.now().isoformat(),
        'feature_count': len(features),
        'training_rows': len(train),
        'test_rows': 0, # Will be updated in evaluate
        'target': target,
        'forecast_horizon': '7 days / 1 week',
        'dataset_version': '1.0'
    }
    
    with open('models/model_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=4)
        
    logger.info("TRAIN pipeline finished")
    return best_model
