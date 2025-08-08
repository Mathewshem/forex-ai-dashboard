import pandas as pd
from datetime import datetime
import os

LOG_FILE = "journal/trade_signals.csv"

def log_signal(symbol, signal_type, score, source="AI Engine"):
    os.makedirs("journal", exist_ok=True)

    new_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": symbol,
        "signal_type": signal_type,  # e.g. BUY, SELL
        "score": score,
        "source": source
    }

    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    else:
        df = pd.DataFrame([new_entry])

    df.to_csv(LOG_FILE, index=False)
