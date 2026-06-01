import yfinance as yf
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def fetch_stock_data(symbol="AAPL", period="1y", interval="1d"):
    """
    Fetches fresh market data for a given symbol from yfinance.
    This ensures fresh data is retrieved for every request.
    """
    try:
        data = yf.download(symbol, period=period, interval=interval, progress=False)
        
        if data.empty:
            logger.warning(f"No market data found for {symbol}")
            return pd.DataFrame()

        # Flatten MultiIndex columns if present (common in newer yfinance versions)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        return data
    except Exception as e:
        logger.error(f"Failed to fetch data for {symbol}: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    # Example usage for historical data (1 year daily)
    data = fetch_stock_data(symbol="AAPL", period="1y", interval="1d")
    print(data.head())

    # Example usage for fetching recent data (e.g., last day, 1-minute interval)
    current_price_data = fetch_stock_data(symbol="AAPL", period="1d", interval="1m")
    if not current_price_data.empty:
        current_price = current_price_data['Close'].iloc[-1]
        print(f"Latest 1-minute close price for AAPL: {current_price}")
    else:
        print("Could not fetch latest 1-minute price for AAPL.")