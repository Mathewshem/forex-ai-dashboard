from forex_python.converter import CurrencyRates
from datetime import datetime

def get_exchange_rate(base='EUR', target='USD'):
    c = CurrencyRates()
    try:
        rate = c.get_rate(base, target)
        print(f"{base}/{target} rate: {rate}")
        return rate
    except Exception as e:
        print("Error fetching exchange rate:", e)
        return None

if __name__ == "__main__":
    get_exchange_rate()
