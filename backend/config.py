import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


MODEL_PATH = os.path.join(BASE_DIR, "models", "saved_model.h5")
SCALER_PATH = os.path.join(BASE_DIR, "models", "scaler.pkl")
RF_MODEL_PATH = os.path.join(BASE_DIR, "models", "rf_model.joblib")
RF_SCALER_PATH = os.path.join(BASE_DIR, "models", "rf_scaler.pkl")

SUPPORTED_SYMBOLS = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corp.",
    "NVDA": "NVIDIA Corp.",
    "TSLA": "Tesla Inc.",
    "AMZN": "Amazon.com Inc."
}