import streamlit as st
import pandas as pd
import sys
import os
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scoring.scoring_engine import score_asset

import plotly.graph_objects as go
import ta
import yfinance as yf

from models.prophet_forecast import forecast_price

import time
import streamlit as st
from datetime import datetime

from utils.journal_logger import log_signal

from models.lstm_predictor import train_lstm_and_predict
from auth.firebase_auth import login



st.set_page_config(layout="wide", page_title="Forex AI Assistant")

st.title("📈 AI-Powered Forex Trade Assistant Dashboard")

symbols = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X",
    "AUDUSD=X", "NZDUSD=X", "BTC-USD", "ETH-USD"
]

st.sidebar.subheader("🔐 Premium Access")

password = st.sidebar.text_input("Enter access code:", type="password")
AUTHORIZED = password == "shem"  # You can change this to anything


st.sidebar.subheader("🔄 Auto-Refresh Settings")

auto_refresh = st.sidebar.checkbox("Enable Auto-Refresh", value=False)
refresh_interval = st.sidebar.selectbox("Refresh Interval", [5, 15, 30, 60], index=3)

if auto_refresh:
    st.sidebar.success(f"Refreshing every {refresh_interval} minutes")
    st_autorefresh = st.experimental_rerun
    last_run = st.session_state.get("last_run", datetime.now())

    elapsed = (datetime.now() - last_run).seconds
    if elapsed >= refresh_interval * 60:
        st.session_state["last_run"] = datetime.now()
        st.experimental_rerun()
else:
    st.session_state["last_run"] = datetime.now()

@st.cache_data(show_spinner=False)
def load_scores():
    data = []
    for symbol in symbols:
        try:
            score = score_asset(symbol)
            data.append(score)
        except Exception as e:
            st.warning(f"Error fetching {symbol}: {e}")
    return pd.DataFrame(data)

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()

df = load_scores()
st.dataframe(df.sort_values(by="score", ascending=False), use_container_width=True)

st.subheader("📊 Asset Technical Chart")

selected_symbol = st.selectbox("Select a symbol to view chart:", options=symbols)

@st.cache_data(ttl=300)
def load_ohlc(symbol):
    df = yf.download(tickers=symbol, interval="1h", period="5d", auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    return df.dropna()

ohlc = load_ohlc(selected_symbol)


# Bollinger Bands
bb = ta.volatility.BollingerBands(close=ohlc['Close'], window=20)
ohlc['bb_upper'] = bb.bollinger_hband()
ohlc['bb_lower'] = bb.bollinger_lband()

# Plotly Candlestick
fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=ohlc.index,
    open=ohlc['Open'],
    high=ohlc['High'],
    low=ohlc['Low'],
    close=ohlc['Close'],
    name='Candles'
))

# Bollinger Band Overlays
fig.add_trace(go.Scatter(
    x=ohlc.index, y=ohlc['bb_upper'],
    line=dict(color='blue', width=1), name='BB Upper'
))
fig.add_trace(go.Scatter(
    x=ohlc.index, y=ohlc['bb_lower'],
    line=dict(color='blue', width=1), name='BB Lower'
))

fig.update_layout(
    title=f"{selected_symbol} - 1H Chart",
    xaxis_rangeslider_visible=False,
    template="plotly_dark",
    height=600
)

st.plotly_chart(fig, use_container_width=True)

#st.subheader("📉 Prophet Forecast")

#raw, prediction = forecast_price(selected_symbol)

#import plotly.graph_objects as go

#fig2 = go.Figure()
#fig2.add_trace(go.Scatter(x=raw['ds'], y=raw['y'], name='Actual', line=dict(color='blue')))
#fig2.add_trace(go.Scatter(x=prediction['ds'], y=prediction['yhat'], name='Forecast', line=dict(color='orange')))
#fig2.add_trace(go.Scatter(x=prediction['ds'], y=prediction['yhat_upper'], name='Upper Bound', line=dict(width=0.5, color='gray')))
#fig2.add_trace(go.Scatter(x=prediction['ds'], y=prediction['yhat_lower'], name='Lower Bound', line=dict(width=0.5, color='gray')))

#fig2.update_layout(
#    height=500,
 #   xaxis_title="Date",
  #  yaxis_title="Price",
   # title=f"{selected_symbol} Price Forecast (Prophet)",
    #template="plotly_white"
#)

#st.plotly_chart(fig2, use_container_width=True)

if AUTHORIZED:
    st.subheader("📉 Prophet Forecast")
    #forecast_type = st.selectbox("Forecast Timeframe", ["Hourly", "Daily"])
    st.info("Only Hourly forecast is supported currently.")
    forecast_type = "Hourly"  # Force selection

    interval = "1h"
    period = "5d"
    horizon = 24

    #if forecast_type == "Hourly":
     #   interval = "1h"
      #  period = "5d"
      #  horizon = 24
    #else:
      #  interval = "1d"
      #  period = "60d"
      #  horizon = 7

    raw, prediction = forecast_price(selected_symbol, interval, period, horizon)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=raw['ds'], y=raw['y'], name='Actual', line=dict(color='blue')))
    fig2.add_trace(go.Scatter(x=prediction['ds'], y=prediction['yhat'], name='Forecast', line=dict(color='orange')))
    fig2.add_trace(go.Scatter(x=prediction['ds'], y=prediction['yhat_upper'], name='Upper Bound',
                              line=dict(width=0.5, color='gray')))
    fig2.add_trace(go.Scatter(x=prediction['ds'], y=prediction['yhat_lower'], name='Lower Bound',
                              line=dict(width=0.5, color='gray')))

    fig2.update_layout(title=f"{selected_symbol} - Prophet Forecast", height=500)
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("🔒 Prophet forecast is locked. Enter access code to unlock.")



st.subheader("📓 Trade Signal Journal")


if os.path.exists("journal/trade_signals.csv"):
    journal_df = pd.read_csv("journal/trade_signals.csv")
    st.dataframe(journal_df.tail(20), use_container_width=True)
else:
    st.info("No trade signals logged yet.")



st.subheader("🧠 LSTM Next-Candle Prediction")

lstm_result = train_lstm_and_predict(selected_symbol)

st.metric(
    label=f"{selected_symbol} LSTM Direction",
    value=f"{lstm_result['predicted_direction']}",
    delta=f"{lstm_result['confidence'] * 100:.2f}% confidence"
)


import glob

st.subheader("📝 Recent Auto-Scoring Summary")

latest_file = max(glob.glob("reports/*.csv"), key=os.path.getctime, default=None)

if latest_file:
    df_summary = pd.read_csv(latest_file)
    st.dataframe(df_summary.sort_values(by="score", ascending=False), use_container_width=True)
else:
    st.info("No reports generated yet.")

# --- Sidebar Login ---
st.sidebar.title("🔐 Login")
email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.sidebar.button("Login"):
    user = login(email, password)
    if user:
        st.session_state["logged_in"] = True
        st.session_state["user_email"] = email
        st.success("✅ Login successful!")
    else:
        st.error("❌ Invalid credentials")

if not st.session_state["logged_in"]:
    st.warning("🚫 Please log in to access premium features.")
    st.stop()

import time
import streamlit as st

# --- Telegram helper (matches our 3-arg call) ---
def send_telegram_message(bot_token: str, chat_id: int | str, text: str, parse_mode: str = "Markdown") -> dict:
    import requests
    if not bot_token or not chat_id:
        raise TypeError("BOT_TOKEN and CHAT_ID must be set (not None/empty).")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": str(chat_id), "text": str(text), "parse_mode": parse_mode}
    r = requests.post(url, json=payload, timeout=15)
    r.raise_for_status()
    return r.json()

# --- Telegram config (from Streamlit secrets) ---
BOT_TOKEN = st.secrets["telegram"]["bot_token"]
CHAT_ID = str(st.secrets["telegram"]["chat_id"])  # group IDs can be negative; keep as string is fine

# ================= Edge-trigger + cooldown guards =================
# Tracks last state per (symbol, kind). Survives reruns within the same session.
if "last_status" not in st.session_state:
    # structure: {(sym, "BUY"/"SELL"/"FBUY"/"FSELL"): {"active": bool, "last_time": float}}
    st.session_state.last_status = {}

COOLDOWN_MIN = 30  # don't resend same (symbol, kind) within 30 minutes

def _cooldown_ok(key: tuple[str, str]) -> bool:
    last_time = st.session_state.last_status.get(key, {}).get("last_time", 0.0)
    return (time.time() - last_time) >= COOLDOWN_MIN * 60

def _mark_sent(key: tuple[str, str]) -> None:
    st.session_state.last_status.setdefault(key, {})
    st.session_state.last_status[key]["last_time"] = time.time()

def _set_active(key: tuple[str, str], value: bool) -> None:
    st.session_state.last_status.setdefault(key, {})
    st.session_state.last_status[key]["active"] = value

def _was_active(key: tuple[str, str]) -> bool:
    return st.session_state.last_status.get(key, {}).get("active", False)

def _rising_edge(prev_active: bool, now_active: bool) -> bool:
    # Send only when condition becomes true (False -> True)
    return (not prev_active) and now_active

# ===================== ALERT LOGIC (edge-triggered) =====================
# NOTE: assumes you already have df populated and log_signal(...) defined
for _, row in df.iterrows():
    sym   = str(row.get("symbol", "")).strip()
    score = float(row.get("score", 0))
    f_sig = int(row.get("forecast_signal", 0))

    # ---------- BUY (score >= 4) ----------
    buy_key = (sym, "BUY")
    buy_now = (score >= 4)
    if _rising_edge(_was_active(buy_key), buy_now) and _cooldown_ok(buy_key):
        msg = f"📈 *BUY Signal*: {sym} → Score: {score:.2f}"
        try:
            send_telegram_message(BOT_TOKEN, CHAT_ID, msg)
            log_signal(sym, "BUY", score)
            _mark_sent(buy_key)
        except Exception as e:
            st.error(f"Failed to send BUY: {e}")
    _set_active(buy_key, buy_now)

    # ---------- SELL (score <= -3) ----------
    sell_key = (sym, "SELL")
    sell_now = (score <= -3)
    if _rising_edge(_was_active(sell_key), sell_now) and _cooldown_ok(sell_key):
        msg = f"📉 *SELL Signal*: {sym} → Score: {score:.2f}"
        try:
            send_telegram_message(BOT_TOKEN, CHAT_ID, msg)
            log_signal(sym, "SELL", score)
            _mark_sent(sell_key)
        except Exception as e:
            st.error(f"Failed to send SELL: {e}")
    _set_active(sell_key, sell_now)

    # ---------- Prophet BUY forecast (forecast_signal == 1) ----------
    fbuy_key = (sym, "FBUY")
    fbuy_now = (f_sig == 1)
    if _rising_edge(_was_active(fbuy_key), fbuy_now) and _cooldown_ok(fbuy_key):
        msg = f"🤖 Prophet AI: {sym} is expected to rise 📈"
        try:
            send_telegram_message(BOT_TOKEN, CHAT_ID, msg)
            log_signal(sym, "BUY Forecast", score, source="Prophet AI")
            _mark_sent(fbuy_key)
        except Exception as e:
            st.error(f"Failed to send forecast BUY: {e}")
    _set_active(fbuy_key, fbuy_now)

    # ---------- Prophet SELL forecast (forecast_signal == -1) ----------
    fsell_key = (sym, "FSELL")
    fsell_now = (f_sig == -1)
    if _rising_edge(_was_active(fsell_key), fsell_now) and _cooldown_ok(fsell_key):
        msg = f"🤖 Prophet AI: {sym} is expected to fall 📉"
        try:
            send_telegram_message(BOT_TOKEN, CHAT_ID, msg)
            log_signal(sym, "SELL Forecast", score, source="Prophet AI")
            _mark_sent(fsell_key)
        except Exception as e:
            st.error(f"Failed to send forecast SELL: {e}")
    _set_active(fsell_key, fsell_now)
