import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from ..config import RF_MODEL_PATH, RF_SCALER_PATH

def train_rf(data, features_list):
    """Trains a Random Forest Regressor to predict the next day's price."""
    # Prepare features and target
    df = data.copy()
    df['Target'] = df['Close'].shift(-1)
    df.dropna(inplace=True)

    X = df[features_list].values
    y = df['Target'].values

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Initialize and train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_scaled, y)

    # Save model and scaler
    joblib.dump(model, RF_MODEL_PATH)
    joblib.dump(scaler, RF_SCALER_PATH)
    return model, scaler

def predict_rf(features_array):
    """Predicts price using the saved Random Forest model."""
    model = joblib.load(RF_MODEL_PATH)
    scaler = joblib.load(RF_SCALER_PATH)
    
    # Scale input and predict
    scaled_features = scaler.transform(features_array)
    prediction = model.predict(scaled_features)
    return prediction[0]