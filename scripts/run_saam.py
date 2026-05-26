import sys
import os
import time
import subprocess

# Ensure project root is on PYTHONPATH
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from main import app
from db.database import init_db
import uvicorn


def check_venv():
    venv_python = os.path.join("venv", "Scripts", "python.exe")
    if not os.path.exists(venv_python):
        print("Virtual environment not found at ./venv")
        sys.exit(1)
    print("Virtual environment detected")


def run_backend():
    print("Starting SAAM backend with command: uvicorn main:app --reload")
    print("*** Don't forget to start ngrok with: start_webhook.py ***")

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    check_venv()
    init_db()
    time.sleep(0.5)
    run_backend()
