import argparse
import sys
import subprocess
from pipeline.logger import get_logger

logger = get_logger()

def run_step(step_name):
    if step_name == 'clean':
        from pipeline.data_processing import clean_pipeline
        clean_pipeline()
    elif step_name == 'features':
        from pipeline.feature_engineering import features_pipeline
        features_pipeline()
    elif step_name == 'split':
        from pipeline.split import split_pipeline
        split_pipeline()
    elif step_name == 'train':
        from pipeline.model_training import train_pipeline
        train_pipeline()
    elif step_name == 'evaluate':
        from pipeline.evaluation import evaluate_pipeline
        evaluate_pipeline()
    elif step_name == 'train_ais':
        from pipeline.vessel_eta_model import train_eta_model
        train_eta_model()
    elif step_name == 'predict':
        logger.info("Running predict step...")
        # Execute the prediction script using the sample data for testing
        subprocess.run([sys.executable, 'predict.py', '--input', 'data/sample/prediction_input.csv'])
    elif step_name == 'plan':
        from pipeline.logistics_optimization import run_logistics_pipeline
        run_logistics_pipeline()
    elif step_name == 'train_master':
        logger.info("Training Master Super ML (CatBoost, LightGBM, RandomForest)...")
        subprocess.run([sys.executable, '-m', 'src.train_master_super_ml'])
    elif step_name in ['serve', 'dashboard', 'api']:
        logger.info("Starting Maritime Intelligence Server on http://127.0.0.1:8000 ...")
        import uvicorn
        uvicorn.run("src.api:app", host="127.0.0.1", port=8000, reload=True)
    elif step_name == 'all':
        run_step('clean')
        run_step('features')
        run_step('split')
        run_step('train')
        run_step('train_master')
        run_step('evaluate')
        run_step('predict')
        run_step('plan')
        logger.info("ALL steps completed successfully.")
    else:
        logger.error(f"Unknown step: {step_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ocean Freight Forecasting ML Pipeline")
    parser.add_argument('command', choices=['clean', 'features', 'split', 'train', 'train_ais', 'train_master', 'evaluate', 'predict', 'plan', 'all', 'serve', 'dashboard', 'api'],
                        help="Pipeline step to execute")
    parser.add_argument('--input', type=str, help="Input CSV for prediction (only used with predict command)")
    
    args = parser.parse_args()
    
    if args.command == 'predict' and args.input:
        subprocess.run([sys.executable, 'predict.py', '--input', args.input])
    else:
        run_step(args.command)

