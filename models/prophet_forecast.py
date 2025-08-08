import pandas as pd
from prophet import Prophet
import yfinance as yf

import yfinance as yf
from prophet import Prophet
import pandas as pd

def forecast_price(symbol='EURUSD=X', interval='1h', period='5d', horizon=24):
    # Download price data
    df = yf.download(tickers=symbol, interval=interval, period=period, auto_adjust=True)

    # Drop multi-index if exists
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)

    # Reset index to expose date column
    df.reset_index(inplace=True)

    # Print columns for debugging
    print("DEBUG >>> df.columns:", df.columns.tolist())

    # ✅ Instead of df[['Datetime', 'Close']], we find the right datetime column
    datetime_col = None
    for col in df.columns:
        if 'date' in col.lower() or 'time' in col.lower():
            datetime_col = col
            break

    if datetime_col is None:
        raise ValueError(f"No datetime column found in columns: {df.columns.tolist()}")

    if 'Close' not in df.columns:
        raise ValueError("'Close' column not found in the data.")

    # Prepare for Prophet
    df = df[[datetime_col, 'Close']].rename(columns={datetime_col: 'ds', 'Close': 'y'})
    df['ds'] = pd.to_datetime(df['ds']).dt.tz_localize(None)
    df.dropna(inplace=True)

    # Forecast
    model = Prophet(daily_seasonality=True)
    model.fit(df)

    freq = 'H' if interval == '1h' else 'D'
    future = model.make_future_dataframe(periods=horizon, freq=freq)
    forecast = model.predict(future)

    return df, forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

def get_forecast_signal(symbol='EURUSD=X', horizon=6):
    df = yf.download(tickers=symbol, interval='1h', period='5d', auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)

    df.reset_index(inplace=True)
    df = df[['Datetime', 'Close']].rename(columns={'Datetime': 'ds', 'Close': 'y'})
    df['ds'] = df['ds'].dt.tz_localize(None)
    df.dropna(inplace=True)

    model = Prophet(daily_seasonality=True)
    model.fit(df)

    future = model.make_future_dataframe(periods=horizon, freq='H')
    forecast = model.predict(future)

    latest_actual = df['y'].iloc[-1]
    future_predicted = forecast[['ds', 'yhat']].iloc[-horizon:]
    future_mean = future_predicted['yhat'].mean()

    diff_pct = (future_mean - latest_actual) / latest_actual * 100

    # Interpret signal
    if diff_pct > 0.3:
        return 1  # Upward bias
    elif diff_pct < -0.3:
        return -1  # Downward bias
    else:
        return 0  # Flat/Uncertain
