import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [symbol, setSymbol] = useState('BTC-USD');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchPrediction = async () => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/predict', { symbol });
      setResult(response.data);
    } catch (error) {
      alert("Error connecting to Backend. Ensure FastAPI is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <header className="navbar">
        <h1>AI Trading Prediction System</h1>
      </header>

      <main className="dashboard">
        <section className="search-section">
          <input 
            type="text" 
            placeholder="Search Stock/Crypto (e.g. AAPL, BTC-USD)" 
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
          />
          <button onClick={fetchPrediction} disabled={loading}>
            {loading ? "Analyzing..." : "Predict"}
          </button>
        </section>

        {result && (
          <div className="result-grid">
            {/* Main Prediction Card */}
            <div className="card prediction-card">
              <div className="price-info">
                <p><strong>Current Price:</strong> ${result.current_price}</p>
                <p><strong>Predicted Price:</strong> ${result.predicted_price}</p>
              </div>
              <div className={`signal-badge ${result.signal.toLowerCase()}`}>
                {result.signal}
              </div>
              <p>Trend: <span className="highlight">{result.trend}</span></p>
              <p>Confidence: {result.confidence}</p>
            </div>

            {/* Technical Indicators */}
            <div className="card info-card">
              <h3>Technical Indicators</h3>
              <ul>
                <li>RSI: {result.indicators.rsi}</li>
                <li>MACD: {result.indicators.macd}</li>
                <li>MA20: {result.indicators.ma20}</li>
              </ul>
            </div>

            {/* Sentiment Analysis */}
            <div className="card info-card">
              <h3>Sentiment Analysis</h3>
              <p>News: {result.sentiment.news}</p>
              <p>Social: {result.sentiment.social}</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;