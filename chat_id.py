import requests
import streamlit as st

TOKEN = st.secrets["telegram"]["bot_token"]
url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
resp = requests.get(url)
print(resp.json())

