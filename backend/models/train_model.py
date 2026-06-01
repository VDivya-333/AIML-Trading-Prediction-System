
from ..data.fetch_data import fetch_stock_data
from ..data.preprocess import preprocess_data
from .lstm_model import build_model
from ..data.indicators import calculate_rsi, moving_average
import pandas as pd
import numpy as np
from .classifier import train_signal_model
from .rf_model import train_rf
from ..config import MODEL_PATH, SCALER_PATH, RF_MODEL_PATH
import joblib


def train(symbol="AAPL", model_type="LSTM"):
    # Fetch data for a specific symbol (e.g., AAPL)
    data = fetch_stock_data(symbol=symbol)

    # Flatten MultiIndex columns if present (common with yfinance)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Calculate technical indicators
    data['RSI'] = calculate_rsi(data)
    data['MA20'] = moving_average(data, window=20)
    data['MA50'] = moving_average(data, window=50)

    # Add dummy sentiment for training history
    data['Sentiment'] = np.random.randint(-1, 2, size=len(data))

    # --- Logic for Logistic Regression Classifier ---
    # Create target labels: 2 (Buy) if price goes up > 1% in 5 days, 
    # 0 (Sell) if down > 1%, 1 (Hold) otherwise.
    future_return = data['Close'].shift(-5) / data['Close'] - 1
    data['Signal'] = 1  # Default Hold
    data.loc[future_return > 0.01, 'Signal'] = 2
    data.loc[future_return < -0.01, 'Signal'] = 0

    # Define features to use for training
    features_list = ['Close', 'Volume', 'RSI', 'MA20', 'MA50', 'Sentiment']

    # Drop any rows with NaN values introduced by indicators
    data.dropna(inplace=True)

    # Prepare classification data before scaling/reshaping for LSTM
    X_classifier = data[['RSI', 'MA20', 'MA50', 'Sentiment']].values
    y_classifier = data['Signal'].values

    # Train Logistic Regression
    print("Training Logistic Regression Classifier...")
    train_signal_model(X_classifier, y_classifier)

    if model_type.upper() == "LSTM":
        # --- Logic for LSTM ---
        x, y, scaler = preprocess_data(data, features_list)
        model = build_model(input_features=len(features_list))
        model.fit(x, y, epochs=5, batch_size=32)
        model.save(MODEL_PATH)
        joblib.dump(scaler, SCALER_PATH)
    elif model_type.upper() == "RANDOMFOREST":
        # --- Logic for Random Forest ---
        train_rf(data, features_list)

    print("Model Trained Successfully")


if __name__ == "__main__":
    train()