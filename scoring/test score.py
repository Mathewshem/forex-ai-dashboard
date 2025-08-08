import yfinance as yf

df = yf.download(tickers='EURUSD=X', interval='1h', period='5d')
df.columns = df.columns.droplevel(1)  # Remove the ticker level

print(df.columns)
print(df.head())
