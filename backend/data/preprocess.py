from sklearn.preprocessing import MinMaxScaler
import numpy as np


def preprocess_data(data, features_list=['Close']):
    scaler = MinMaxScaler(feature_range=(0, 1))
    
    # Ensure all features in features_list are present and handle NaNs
    data_to_scale = data[features_list].dropna()

    # Fit and transform the selected features
    scaled_data = scaler.fit_transform(data_to_scale)

    x = []
    y = []

    # Assuming 'Close' is always the target for prediction, and it's the first feature in features_list
    for i in range(60, len(scaled_data)): # 60 is the sequence length
        x.append(scaled_data[i-60:i, :]) # Take all features for the sequence
        y.append(scaled_data[i, 0])      # Predict the 'Close' price (first feature)

    x = np.array(x)
    y = np.array(y)

    x = np.reshape(x, (x.shape[0], x.shape[1], len(features_list)))

    return x, y, scaler