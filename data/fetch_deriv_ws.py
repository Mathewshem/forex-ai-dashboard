import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    if "tick" in data:
        symbol = data["tick"]["symbol"]
        price = data["tick"]["quote"]
        print(f"{symbol} live price: {price}")

def on_error(ws, error):
    print("Error:", error)

def on_close(ws):
    print("Connection closed.")

def on_open(ws):
    # Change symbol as needed: R_100, R_50, 1HZ100V, etc.
    payload = {
        "ticks": "frxEURUSD",
        "subscribe": 1
    }
    ws.send(json.dumps(payload))

if __name__ == "__main__":
    ws = websocket.WebSocketApp("wss://ws.binaryws.com/websockets/v3?app_id=1089",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()
