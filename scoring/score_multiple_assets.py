from scoring_engine import score_asset
import pandas as pd

symbols = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X",
    "AUDUSD=X", "NZDUSD=X", "BTC-USD", "ETH-USD"
]

all_scores = []

for symbol in symbols:
    try:
        result = score_asset(symbol)
        all_scores.append(result)
    except Exception as e:
        print(f"Error scoring {symbol}: {e}")

# Convert to DataFrame
df = pd.DataFrame(all_scores)
print(df.sort_values(by="score", ascending=False))
