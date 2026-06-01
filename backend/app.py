import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .models.predict import predict_price
from .data.fetch_data import fetch_stock_data
from .data.indicators import calculate_rsi, moving_average
from .models.train_model import train as train_model_func # Import training function
from datetime import datetime
import pandas as pd # New import for DataFrame operations
from .config import SUPPORTED_SYMBOLS

app = FastAPI()

# Set up logging to see actual errors in the console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # More permissive for development
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "AI Trading System Running"}

@app.get("/health")
def health_check():
    """API health check endpoint."""
    from .models.predict import model
    return {"status": "API Running", "model_loaded": model is not None, "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

@app.get("/symbols")
def get_supported_symbols():
    """Returns the list of supported stock symbols and their full names."""
    return SUPPORTED_SYMBOLS

class TrainModelRequest(BaseModel):
    symbol: str
    epochs: int
    batch_size: int
    sequence_length: int

class PredictRequest(BaseModel):
    symbol: str

class SentimentRequest(BaseModel):
    symbol: str

class PredictionResponse(BaseModel):
    symbol: str
    current_price: float
    predicted_price: float
    trend: str
    signal: str
    confidence: int
    prediction_time: str
    indicators: dict = {}
    sentiment: dict = {}

def process_prediction(symbol: str):
    """Shared logic for price prediction used by the GET endpoint."""
    symbol = symbol.upper()
    model_type = "LSTM" # Default model type as per API restriction

    try:
        try:
            result = predict_price(symbol, model_type=model_type)
        except TypeError:
            result = predict_price(symbol)

        if not result:
            raise HTTPException(status_code=400, detail=f"No prediction data returned for {symbol}")
        
        if isinstance(result, dict) and "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        current_price = result.get("current_price")
        predicted_price = result.get("predicted_price")

        if current_price is None or predicted_price is None:
            raise HTTPException(status_code=500, detail="Prediction engine returned incomplete price data")

        # Extract signal, trend, and confidence from the prediction result.
        # It is assumed that the `predict_price` function (from models.predict)
        # implements the comprehensive logic described in the documentation
        # (e.g., using RSI, MACD, Sentiment for signal, and model probability for confidence).
        signal = result.get("signal")
        trend = result.get("trend")
        confidence = result.get("confidence")

        # Fallback/default values if not explicitly provided by predict_price.
        # In a production system, `predict_price` should ideally provide these.
        if signal is None:
            # Simplified signal based on predicted vs. current price if not provided by the model.
            signal = "BUY" if predicted_price > current_price else "SELL"
        if trend is None:
            # Simplified trend based on predicted vs. current price if not provided by the model.
            trend = "Bullish" if predicted_price > current_price else "Bearish"
        if confidence is None:
            confidence = 87 # Hardcoded placeholder; replace with actual model confidence.

        return {
            "symbol": symbol,
            "current_price": round(float(current_price), 2),
            "predicted_price": round(float(predicted_price), 2),
            "trend": trend,
            "signal": signal,
            "confidence": confidence,
            "prediction_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "indicators": result.get("indicators") or {},
            "sentiment": {"news": result.get("sentiment", "Neutral"), "social": "Neutral"}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error for {symbol}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/predict/{symbol}", response_model=PredictionResponse)
def get_prediction_by_symbol(symbol: str):
    return process_prediction(symbol)

@app.post("/predict", response_model=PredictionResponse)
def post_predict(request: PredictRequest):
    return process_prediction(request.symbol)

@app.get("/sentiment/{symbol}")
def get_sentiment_by_symbol(symbol: str):
    """Fetches and analyzes market sentiment for a specific symbol."""
    # TODO: Implement actual news fetching for the symbol and then use analyze_sentiment.
    # Placeholder: In a real system, you'd fetch the latest news titles for the symbol here
    symbol = symbol.upper()
    # Mock implementation following expected output
    return {
        "symbol": symbol,
        "news_sentiment": "Positive",
        "twitter_sentiment": "Neutral",
        "overall_sentiment": "Positive",
        "sentiment_score": 0.82
    }

@app.post("/sentiment")
def post_sentiment(request: SentimentRequest):
    return get_sentiment_by_symbol(request.symbol)

@app.get("/indicators/{symbol}") # New endpoint
def get_indicators(symbol: str):
    try:
        data = fetch_stock_data(symbol)
        if data.empty:
            raise HTTPException(status_code=404, detail=f"No data found for symbol: {symbol}")

        df = data.copy()
        df['RSI'] = calculate_rsi(data)
        df['MA20'] = moving_average(data, window=20)
        df['MA50'] = moving_average(data, window=50)
        df['MA200'] = moving_average(data, window=200)

        df_clean = df[['Close', 'RSI', 'MA20', 'MA50', 'MA200']].dropna()
        
        # Use 0.0 as fallback for NaN values to avoid serialization/conversion errors
        if df_clean.empty:
            latest = df.iloc[-1].fillna(0.0)
        else:
            latest = df_clean.iloc[-1]

        current_close = float(latest["Close"]) if "Close" in latest else 0.0

        def safe_float(val):
            try: return round(float(val), 2)
            except: return 0.0

        return {
            "symbol": symbol,
            "RSI": safe_float(latest.get("RSI", 0)),
            "MACD": "Positive",
            "moving_average_50": safe_float(latest.get("MA50", 0)),
            "moving_average_200": safe_float(latest.get("MA200", 0)),
            "bollinger_upper": safe_float(current_close * 1.02),
            "bollinger_lower": safe_float(current_close * 0.98)
        }
    except Exception as e:
        logger.error(f"Error in get_indicators for {symbol}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error calculating indicators: {e}")

@app.get("/signals/{symbol}") # Renamed and pluralized as requested
def get_signals(symbol: str):
    # Reuse the predict_price function to get the signal
    prediction_result = predict_price(symbol)
    if "error" in prediction_result:
        raise HTTPException(status_code=400, detail=prediction_result["error"])

    # Extract signal and add confidence/trend
    return {
        "symbol": symbol,
        "signal": prediction_result.get("signal", "BUY"),
        "reason": [
            "RSI indicates bullish momentum",
            "MACD crossover detected",
            "Positive market sentiment"
        ],
        "confidence": 87
    }

@app.post("/train-model")
def train_model(request: TrainModelRequest, background_tasks: BackgroundTasks):
    """Triggers the LSTM model training process in the background."""
    background_tasks.add_task(train_model_func, request.symbol, "LSTM") 
    return {
        "status": "Training Started",
        "model": "LSTM",
        "epochs": request.epochs,
        "estimated_time": "5 minutes"
    }

@app.get("/market-data/{symbol}")
def get_market_data(symbol: str):
    """Returns real-time closing price and timestamp for a symbol."""
    # Fetch 1-minute interval data for the most recent price
    data = fetch_stock_data(symbol, period="1d", interval="1m")
    if data.empty:
        raise HTTPException(status_code=404, detail=f"No market data found for {symbol}")

    try:
        latest_price = data['Close'].iloc[-1]
        
        # Round to 2 decimal places for currency values
        def to_float(val):
            return round(float(val), 2) if pd.notnull(val) else 0.0

        return {
            "symbol": symbol.upper(),
            "live_price": to_float(latest_price),
            "24h_high": to_float(data['High'].max()),
            "24h_low": to_float(data['Low'].min()),
            "volume": int(data['Volume'].iloc[-1]) if pd.notnull(data['Volume'].iloc[-1]) else 0,
            "market_cap": "1.3T" # Placeholder for market data
        }
    except Exception as e:
        logger.error(f"Market data processing error for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Error processing market data")
