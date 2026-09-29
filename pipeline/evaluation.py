import pandas as pd
import numpy as np
import joblib
import json
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from .logger import get_logger

logger = get_logger()

def mean_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    non_zero = y_true != 0
    return np.mean(np.abs((y_true[non_zero] - y_pred[non_zero]) / y_true[non_zero])) * 100

def evaluate_pipeline():
    logger.info("Starting EVALUATE pipeline")
    
    test = pd.read_csv('data/test/test.csv')
    train = pd.read_csv('data/training/train.csv')
    val = pd.read_csv('data/training/val.csv')
    master = pd.read_csv('data/processed/featured_dataset.csv')
    
    preprocessor = joblib.load('models/preprocessor.joblib')
    model = joblib.load('models/freight_model.joblib')
    
    with open('models/model_metadata.json', 'r') as f:
        metadata = json.load(f)
        
    target = metadata.get('target', 'target_next_week')
    features = [c for c in test.columns if c not in ['date', 'route', target]]
    
    X_test = test[features]
    y_test = test[target]
    
    X_test_prep = preprocessor.transform(X_test)
    preds = model.predict(X_test_prep)
    
    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)
    mape = mean_absolute_percentage_error(y_test, preds)
    
    metrics = [{
        'model_name': metadata.get('model_name', 'Unknown'),
        'MAE': mae,
        'RMSE': rmse,
        'R2': r2,
        'MAPE': mape,
        'training_rows': len(train),
        'validation_rows': len(val),
        'test_rows': len(test)
    }]
    
    pd.DataFrame(metrics).to_csv('reports/model_metrics.csv', index=False)
    
    metadata['MAE'] = mae
    metadata['RMSE'] = rmse
    metadata['R2'] = r2
    metadata['test_rows'] = len(test)
    
    with open('models/model_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=4)
        
    logger.info(f"Test MAE: {mae:.2f}, RMSE: {rmse:.2f}, R2: {r2:.4f}")
    
    # Generate final dataset report
    dataset_report = {
        'total_rows': len(master),
        'total_columns': len(master.columns),
        'date_min': master['date'].min(),
        'date_max': master['date'].max(),
        'missing_values': int(master.isnull().sum().sum()),
        'duplicate_count': int(master.duplicated().sum()),
        'outlier_count': int(sum([master[c].sum() for c in master.columns if 'is_outlier' in c])),
        'target_statistics': {
            'mean': float(master[target].mean()),
            'median': float(master[target].median()),
            'std': float(master[target].std())
        },
        'feature_count': len(features),
        'route_count': int(master['route'].nunique()),
        'container_type_count': int(master['container_type'].nunique()) if 'container_type' in master.columns else 0
    }
    
    with open('reports/final_dataset_report.json', 'w') as f:
        json.dump(dataset_report, f, indent=4)
        
    logger.info("EVALUATE pipeline finished")
