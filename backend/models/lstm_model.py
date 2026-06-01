from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input


def build_model(input_features=1):
    model = Sequential()
    model.add(Input(shape=(60, input_features)))
    model.add(LSTM(64, return_sequences=True))
    model.add(Dropout(0.2))

    model.add(LSTM(64))
    model.add(Dropout(0.2))

    model.add(Dense(1))

    model.compile(optimizer='adam', loss='mean_squared_error')

    return model