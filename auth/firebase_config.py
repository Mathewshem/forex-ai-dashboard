import pyrebase
import streamlit as st

firebase_config = {
    "apiKey": st.secrets["firebase"]["api_key"],
    "authDomain": st.secrets["firebase"]["auth_domain"],
    "projectId": st.secrets["firebase"]["project_id"],
    "storageBucket": st.secrets["firebase"]["storage_bucket"],
    "messagingSenderId": st.secrets["firebase"]["messaging_sender_id"],
    "appId": st.secrets["firebase"]["app_id"],
    "measurementId": st.secrets["firebase"]["measurement_id"],
    "databaseURL": ""  # Optional: Only needed for real-time DB
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
