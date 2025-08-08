import requests

TOKEN = '8230694522:AAGtK_pPK_g7nIyt1y7F62CsgGDMFTcZ6cU'
url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
resp = requests.get(url)
print(resp.json())

