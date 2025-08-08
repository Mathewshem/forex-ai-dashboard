import pyrebase

firebase_config = {
    "apiKey": "AIzaSyBa4-3q9biWgxXyDB7C0sJi_imye2_f6lM",
    "authDomain": "forexai-dashboard-4413b.firebaseapp.com",
    "projectId": "forexai-dashboard-4413b",
    "storageBucket": "forexai-dashboard-4413b.appspot.com",
    "messagingSenderId": "781579143280",
    "appId": "1:781579143280:web:012fa56ee10f07d4d10cb5",
    "measurementId": "G-GLVVJWRVFN",
    "databaseURL": "https://forexai-dashboard-4413b.firebaseio.com"
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# --- Test Logins ---
test_users = [
    ("mathewshem@yahoo.com", "test1234"),
    ("mathewshem90@gmail.com", "test1234")
]

for email, password in test_users:
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        print(f"✅ Login successful for {email}")
    except Exception as e:
        print(f"❌ Login failed for {email}")
        print(e)
