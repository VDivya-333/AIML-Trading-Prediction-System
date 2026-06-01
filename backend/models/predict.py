from tensorflow.keras.models import load_model # pyright: ignore[reportMissingModuleSource]
from ..data.fetch_data import fetch_stock_data
from ..data.preprocess import preprocess_data
from ..data.indicators import calculate_rsi, moving_average
from ..signals.signal_generator import generate_signal
from ..sentiment.news_sentiment import analyze_sentiment
import numpy as np
import pandas as pd
from ..config import MODEL_PATH, SCALER_PATH
import joblib
import logging

logger = logging.getLogger(__name__)

model = None
scaler = None

def load_components():
    global model, scaler
    if model is None:
        try:
            model = load_model(MODEL_PATH)
            logger.info("Model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
    if scaler is None:
        try:
            scaler = joblib.load(SCALER_PATH)
            logger.info("Scaler loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load scaler: {e}")

def predict_price(symbol="AAPL"):
    load_components()
    if model is None or scaler is None:
        return {"error": "Prediction components not loaded. Please ensure training is complete."}

    data = fetch_stock_data(symbol)

    if data is None or data.empty:
        return {"error": f"No data found for symbol {symbol}."}

    # Flatten MultiIndex columns if present (e.g., from yfinance)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # 2. Calculate technical indicators
    data['RSI'] = calculate_rsi(data)
    data['MA20'] = moving_average(data, window=20)
    data['MA50'] = moving_average(data, window=50)

    # 3. Placeholder for fetching news and performing sentiment analysis
    # In a real system, you'd fetch recent news for the 'symbol'
    sample_news_text = "The market for " + symbol + " is showing strong growth today."
    sentiment_result = analyze_sentiment(sample_news_text)
    sentiment_label = sentiment_result.get("sentiment", "Neutral")
    # Convert sentiment to a numerical value for the model (e.g., Positive=1, Neutral=0, Negative=-1)
    sentiment_map = {"Positive": 1, "Neutral": 0, "Negative": -1}
    data['Sentiment'] = sentiment_map.get(sentiment_label, 0) # Add sentiment as a feature

    # Define features to use for prediction (must match training features)
    features_list = ['Close', 'Volume', 'RSI', 'MA20', 'MA50', 'Sentiment']

    # Drop any rows with NaN values introduced by indicators
    data.dropna(inplace=True)

    # 4. Transform data using the LOADED scaler
    scaled_data = scaler.transform(data[features_list])
    
    if len(scaled_data) < 60:
        return {"error": f"Not enough data after indicator calculation. Need 60, got {len(scaled_data)}"}

    # Create sequence for the last 60 days
    last_sequence = scaled_data[-60:]
    x_input = last_sequence.reshape(1, 60, len(features_list))

    # Make prediction
    prediction = model.predict(x_input)

    # Inverse transform the prediction (only for the 'Close' price, which is the first feature)
    # Create a dummy array with the predicted 'Close' and zeros for other features for inverse_transform
    dummy_prediction_input = np.zeros((1, len(features_list)))
    dummy_prediction_input[0, 0] = prediction[0, 0] # Place predicted 'Close' in the first column
    
    # Unscale the predicted price back to original market value
    predicted_price = float(scaler.inverse_transform(dummy_prediction_input)[0, 0])

    # Get the actual last closing price. Handle potential Series if columns are MultiIndex (common with yfinance)
    last_val = data['Close'].iloc[-1]
    current_price = float(last_val.iloc[0] if hasattr(last_val, 'iloc') else last_val)

    signal = generate_signal(predicted_price, current_price)

    # Extract technical indicators for the response
    indicators = {
        "rsi": float(data['RSI'].iloc[-1]),
        "ma20": float(data['MA20'].iloc[-1]),
        "ma50": float(data['MA50'].iloc[-1])
    }

    # Calculate a basic confidence score based on the trend strength
    price_diff_pct = abs((predicted_price - current_price) / current_price)
    # Higher difference in a volatile market might lower confidence, but here we use it as signal strength
    confidence = min(int(80 + (price_diff_pct * 100)), 98)

    return {
        "symbol": symbol,
        "current_price": current_price,
        "predicted_price": predicted_price,
        "signal": signal,
        "confidence": confidence,
        "sentiment": sentiment_label, # Return the string label for the frontend
        "indicators": indicators
    }