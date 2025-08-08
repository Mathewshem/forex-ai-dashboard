import pyrebase

firebase_config = {
    "apiKey": "AIzaSyBa4-3q9biWgxXyDB7C0sJi_imye2_f6lM",
    "authDomain": "forexai-dashboard-4413b.firebaseapp.com",
    "projectId": "forexai-dashboard-4413b",
    "storageBucket": "forexai-dashboard-4413b.appspot.com",  # FIXED typo (.app → .appspot.com)
    "messagingSenderId": "781579143280",
    "appId": "1:781579143280:web:012fa56ee10f07d4d10cb5",
    "measurementId": "G-GLVVJWRVFN",
    "databaseURL": ""  # leave this empty unless using realtime DB
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
