@echo off
echo ========================================================
echo NAVIQ MARITIME - MASTER SUPER ML ^& FASTAPI SERVER RUNNER
echo ========================================================
echo.
echo [1/2] Training Master Super ML Models...
python src\train_master_super_ml.py

echo.
echo [2/2] Starting Backend API Server ^& Live Tracking...
set PYTHONPATH=.
python -m src.api
