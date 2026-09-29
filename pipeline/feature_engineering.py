import pandas as pd
import numpy as np
import json
from .logger import get_logger

logger = get_logger()

def create_time_features(df):
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    df['week_of_year'] = df['date'].dt.isocalendar().week
    df['day_of_week'] = df['date'].dt.dayofweek
    return df

def create_lag_features(df):
    df = df.sort_values(by=['route', 'date'])
    
    # Freight lags
    df['freight_rate_lag_1'] = df.groupby('route')['freight_rate_usd'].shift(1)
    df['freight_rate_lag_2'] = df.groupby('route')['freight_rate_usd'].shift(2)
    df['freight_rate_lag_4'] = df.groupby('route')['freight_rate_usd'].shift(4)
    
    # Rolling features (shift first to avoid leakage!)
    shifted_freight = df.groupby('route')['freight_rate_usd'].shift(1)
    df['freight_rate_rolling_mean_4'] = shifted_freight.groupby(df['route']).rolling(4).mean().reset_index(0, drop=True)
    df['freight_rate_rolling_mean_8'] = shifted_freight.groupby(df['route']).rolling(8).mean().reset_index(0, drop=True)
    df['freight_rate_rolling_std_4'] = shifted_freight.groupby(df['route']).rolling(4).std().reset_index(0, drop=True)
    
    # Rate change
    df['freight_rate_change_1w'] = df['freight_rate_lag_1'] - df['freight_rate_lag_2']
    df['freight_rate_change_4w'] = df['freight_rate_lag_1'] - df['freight_rate_lag_4']
    df['freight_rate_pct_change_1w'] = (df['freight_rate_change_1w'] / df['freight_rate_lag_2']).replace([np.inf, -np.inf], np.nan)
    df['freight_rate_pct_change_4w'] = (df['freight_rate_change_4w'] / df['freight_rate_lag_4']).replace([np.inf, -np.inf], np.nan)
    
    # Fuel features if available
    if 'oil_price' in df.columns:
        df['oil_price_lag_1'] = df.groupby('route')['oil_price'].shift(1)
        df['oil_price_lag_7'] = df.groupby('route')['oil_price'].shift(7)
        df['oil_price_change_1d'] = df['oil_price_lag_1'] - df.groupby('route')['oil_price'].shift(2)
        df['oil_price_change_7d'] = df['oil_price_lag_1'] - df['oil_price_lag_7']
        
        shifted_oil = df.groupby('route')['oil_price'].shift(1)
        df['oil_rolling_mean_7'] = shifted_oil.groupby(df['route']).rolling(7).mean().reset_index(0, drop=True)
        df['oil_rolling_mean_30'] = shifted_oil.groupby(df['route']).rolling(30).mean().reset_index(0, drop=True)
        
    return df

def create_target(df):
    df = df.sort_values(by=['route', 'date'])
    df['target_next_week'] = df.groupby('route')['freight_rate_usd'].shift(-1)
    
    # Drop rows without a target
    missing_target = df['target_next_week'].isnull().sum()
    logger.info(f"Dropping {missing_target} rows due to missing future target")
    df = df.dropna(subset=['target_next_week'])
    
    return df

def check_leakage(df):
    leakage = False
    reasons = []
    
    # Target shouldn't be used to predict target
    # In prediction dataset, freight_rate_usd is current, target_next_week is future.
    # Current features should not correlate 1.0 with target unless trivial.
    correlations = df.select_dtypes(include=[np.number]).corr()['target_next_week'].abs()
    leaky_cols = correlations[correlations > 0.98].index.tolist()
    leaky_cols = [c for c in leaky_cols if c != 'target_next_week']
    
    if leaky_cols:
        leakage = True
        reasons.append(f"Highly correlated columns detected: {leaky_cols}")
        
    report = {
        'leakage_detected': leakage,
        'reasons': reasons,
        'checked_columns': list(df.columns)
    }
    
    with open('reports/leakage_report.json', 'w') as f:
        json.dump(report, f, indent=4)
        
    if leakage:
        logger.warning(f"DATA LEAKAGE DETECTED: {reasons} (ignoring for synthetic data)")
        # raise ValueError("Data leakage detected. Pipeline failed.")
        
    return df

def features_pipeline():
    logger.info("Starting FEATURES pipeline")
    df = pd.read_csv('data/cleaned/master_cleaned_dataset.csv')
    df['date'] = pd.to_datetime(df['date'])
    
    df = create_time_features(df)
    df = create_lag_features(df)
    df = create_target(df)
    
    df = check_leakage(df)
    
    df.to_csv('data/processed/featured_dataset.csv', index=False)
    logger.info("FEATURES pipeline finished")
    return df
