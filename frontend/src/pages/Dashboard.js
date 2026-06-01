import React, { useEffect, useState } from "react";
import axios from "axios";

function Dashboard() {
  const [prediction, setPrediction] = useState({});

  useEffect(() => {
    fetchPrediction();
  }, []);

  const fetchPrediction = async () => {
    const res = await axios.get("http://localhost:8000/predict/BTCUSDT");
    setPrediction(res.data);
  };

  return (
    <div>
      <h1>AI Trading Dashboard</h1>

      <div>
        <h2>Asset: {prediction.symbol}</h2>
        <p>Current Price: {prediction.current_price}</p>
        <p>Predicted Price: {prediction.predicted_price}</p>
        <p>Signal: {prediction.signal}</p>
        <p>Confidence: {prediction.confidence}%</p>
      </div>
    </div>
  );
}

export default Dashboard;