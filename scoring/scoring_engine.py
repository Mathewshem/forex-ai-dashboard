import yfinance as yf
import pandas as pd
import numpy as np
import ta
from models.prophet_forecast import get_forecast_signal


def fetch_ohlc(symbol='EURUSD=X', interval='1h', period='5d'):
    data = yf.download(tickers=symbol, interval=interval, period=period, auto_adjust=True)

    # Drop the ticker level from multi-index
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)

    return data


def calculate_z_score(series, window=20):
    mean = series.rolling(window).mean()
    std = series.rolling(window).std()
    z_score = (series - mean) / std
    return z_score


def calculate_atr(data, period=14):
    required_cols = ['High', 'Low', 'Close']
    if not all(col in data.columns for col in required_cols):
        return np.nan

    data = data.dropna(subset=required_cols)
    if data.empty or len(data) < period:
        return np.nan

    atr = ta.volatility.AverageTrueRange(high=data['High'],
                                          low=data['Low'],
                                          close=data['Close'],
                                          window=period)
    return atr.average_true_range().iloc[-1]


def calculate_adr(data, period=14):
    if 'High' not in data or 'Low' not in data:
        return np.nan
    data['ADR'] = data['High'] - data['Low']
    return data['ADR'].rolling(period).mean().iloc[-1]


def calculate_trend_strength(data):
    if len(data) < 10:
        return 0
    if data['Close'].iloc[-1] > data['Close'].iloc[-10]:
        return 1
    elif data['Close'].iloc[-1] < data['Close'].iloc[-10]:
        return -1
    else:
        return 0


def score_asset(symbol='EURUSD=X'):
    df = fetch_ohlc(symbol)
    df.dropna(inplace=True)

    # TA indicators
    rsi = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi().iloc[-1]
    macd = ta.trend.MACD(close=df['Close']).macd_diff().iloc[-1]
    bb = ta.volatility.BollingerBands(close=df['Close'], window=20, window_dev=2)
    bb_score = bb.bollinger_hband().iloc[-1] - bb.bollinger_lband().iloc[-1]

    # Other indicators
    z = calculate_z_score(df['Close']).dropna().iloc[-1] if len(df['Close'].dropna()) > 20 else 0
    atr = calculate_atr(df)
    adr = calculate_adr(df)
    trend = calculate_trend_strength(df)

    # Placeholder for COT and Retail Sentiment (to be integrated in Phase 3)
    retail_sentiment_score = 0
    cot_positioning_score = 0

    # Scoring logic
    score = 0
    score += trend * 2
    score += 1 if z < -1 else (-1 if z > 1 else 0)
    score += 1 if adr > atr else 0
    score += 1 if macd > 0 else -1
    score += 1 if rsi < 30 else (-1 if rsi > 70 else 0)
    score += retail_sentiment_score + cot_positioning_score
    forecast_score = get_forecast_signal(symbol)
    score += forecast_score

    result = {
        "symbol": symbol,
        "z_score": round(z, 2),
        "adr": round(adr, 4),
        "atr": round(atr, 4),
        "trend": trend,
        "rsi": round(rsi, 2),
        "macd": round(macd, 4),
        "bb_width": round(bb_score, 4),
        "forecast_signal": forecast_score,
        "score": score
    }

    return result


if __name__ == "__main__":
    print(score_asset("EURUSD=X"))
