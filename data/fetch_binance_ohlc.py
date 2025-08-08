import requests
import pandas as pd

def fetch_binance_ohlc(symbol='BTCUSDT', interval='1h', limit=100):
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}'
    response = requests.get(url)

    if response.status_code == 200:
        raw_data = response.json()
        df = pd.DataFrame(raw_data, columns=[
            'Open time', 'Open', 'High', 'Low', 'Close', 'Volume',
            'Close time', 'Quote asset volume', 'Number of trades',
            'Taker buy base', 'Taker buy quote', 'Ignore'
        ])
        df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
        df.set_index('Open time', inplace=True)
        print(df[['Open', 'High', 'Low', 'Close']].tail())
        return df
    else:
        print("Error:", response.status_code)
        return None

if __name__ == "__main__":
    fetch_binance_ohlc()
