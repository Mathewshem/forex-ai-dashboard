import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense


def fetch_ohlc(symbol='EURUSD=X', interval='1h', period='30d'):
    df = yf.download(tickers=symbol, interval=interval, period=period, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    df = df[['Close']].dropna()
    return df


def create_lstm_dataset(series, window_size=24):
    X, y = [], []
    for i in range(window_size, len(series)):
        X.append(series[i - window_size:i])
        y.append(1 if series[i] > series[i - 1] else 0)  # 1 = UP, 0 = DOWN
    return np.array(X), np.array(y)


def train_lstm_and_predict(symbol='EURUSD=X'):
    df = fetch_ohlc(symbol)

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df[['Close']].values)

    X, y = create_lstm_dataset(scaled, window_size=24)
    X = X.reshape((X.shape[0], X.shape[1], 1))

    model = Sequential()
    model.add(LSTM(units=50, input_shape=(X.shape[1], 1)))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    model.fit(X, y, epochs=5, batch_size=16, verbose=0)

    last_input = scaled[-24:].reshape((1, 24, 1))
    prediction = model.predict(last_input)

    return {
        'symbol': symbol,
        'predicted_direction': 'UP' if prediction[0][0] >= 0.5 else 'DOWN',
        'confidence': round(float(prediction[0][0]), 3)
    }


#This is a minimal LSTM. You can expand it later with:

#Volatility as target

#OHLC inputs instead of Close only

#Multi-currency batch training

