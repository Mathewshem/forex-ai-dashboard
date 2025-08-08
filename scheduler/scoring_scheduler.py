import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time
import os

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

from scoring.scoring_engine import score_asset
from models.lstm_predictor import train_lstm_and_predict

symbols = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X",
    "AUDUSD=X", "NZDUSD=X", "BTC-USD", "ETH-USD"
]

def run_scheduled_scoring():
    results = []

    for symbol in symbols:
        try:
            score = score_asset(symbol)
            lstm = train_lstm_and_predict(symbol)
            entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "symbol": symbol,
                "score": score["score"],
                "trend": score["trend"],
                "rsi": score["rsi"],
                "macd": score["macd"],
                "direction": lstm["predicted_direction"],
                "confidence": lstm["confidence"]
            }
            results.append(entry)
        except Exception as e:
            print(f"Error scoring {symbol}: {e}")

    os.makedirs("reports", exist_ok=True)
    df = pd.DataFrame(results)
    filename = f"reports/scoring_log_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    df.to_csv(filename, index=False)
    print(f"[✓] Saved scoring snapshot: {filename}")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_scheduled_scoring, 'interval', minutes=60)  # runs every hour
    scheduler.start()
    print("✅ Scheduler started")

    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler stopped")
