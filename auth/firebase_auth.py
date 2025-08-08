# auth/firebase_auth.py
from auth.firebase_config import auth

def login(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return user
    except:
        return None
