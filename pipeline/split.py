import pandas as pd
from .logger import get_logger

logger = get_logger()

def split_pipeline():
    logger.info("Starting SPLIT pipeline")
    df = pd.read_csv('data/processed/featured_dataset.csv')
    df['date'] = pd.to_datetime(df['date'])
    
    # Sort by date
    df = df.sort_values(by='date')
    
    total_rows = len(df)
    train_end = int(total_rows * 0.7)
    val_end = int(total_rows * 0.85)
    
    train = df.iloc[:train_end]
    val = df.iloc[train_end:val_end]
    test = df.iloc[val_end:]
    
    logger.info(f"Train dates: {train['date'].min().date()} to {train['date'].max().date()} ({len(train)} rows)")
    logger.info(f"Val dates: {val['date'].min().date()} to {val['date'].max().date()} ({len(val)} rows)")
    logger.info(f"Test dates: {test['date'].min().date()} to {test['date'].max().date()} ({len(test)} rows)")
    
    train.to_csv('data/training/train.csv', index=False)
    val.to_csv('data/training/val.csv', index=False)
    test.to_csv('data/test/test.csv', index=False)
    
    # Save a master training dataset as requested: data/training/ml_training_dataset.csv
    # It should include all engineered features and target. We'll use train + val or just the full processed dataset?
    # Prompt: "Create data/training/ml_training_dataset.csv. It should contain ... all engineered features ... target_next_week"
    # I'll save the whole featured dataset here, or just train set. Let's just save the train set as ml_training_dataset.csv as well.
    train.to_csv('data/training/ml_training_dataset.csv', index=False)
    
    logger.info("SPLIT pipeline finished")
    return train, val, test
