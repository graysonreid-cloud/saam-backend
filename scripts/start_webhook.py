import os
import subprocess
import requests
import time

print("Killing any existing ngrok processes...")
try:
    subprocess.run(["taskkill", "/F", "/IM", "ngrok.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Existing ngrok processes terminated")
except Exception:
    print("ngrok not running")

# 1. Start ngrok
ngrok = subprocess.Popen(["ngrok", "http", "8000"])

# 2. Wait for ngrok to initialize
time.sleep(2)

# 3. Retry loop to fetch the public URL
public_url = None
for _ in range(10):
    try:
        tunnels = requests.get("http://127.0.0.1:4042/api/tunnels").json()
        public_url = tunnels["tunnels"][0]["public_url"]
        break
    except Exception:
        time.sleep(1)

if public_url:
    print(f"NGROK URL: {public_url}")
else:
    print("Could not fetch ngrok URL after retries")
