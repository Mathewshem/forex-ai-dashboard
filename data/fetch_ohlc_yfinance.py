import yfinance as yf

def fetch_ohlc(symbol='EURUSD=X', interval='1h', period='1d'):
    """
    symbol examples:
    - EURUSD=X
    - GBPUSD=X
    - USDJPY=X
    """
    try:
        data = yf.download(tickers=symbol, interval=interval, period=period)
        print(data.tail())
        return data
    except Exception as e:
        print("Error fetching OHLC data:", e)
        return None

if __name__ == "__main__":
    fetch_ohlc()
