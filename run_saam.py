import os
import subprocess
import sys
import time
from db.db_models import init_db

# Create tables on startup
init_db()


def check_venv():
    venv_python = os.path.join("venv", "Scripts", "python.exe")
    if not os.path.exists(venv_python):
        print("❌ Virtual environment not found at ./venv")
        print("Create it with: python -m venv venv")
        sys.exit(1)
    print("Virtual environment detected")

def run_backend():
    print("Starting SAAM backend: - Using command: uvicorn main:app --reload")
    print("*** Dont forget to start ngrok with: start_webhook.py ***")

    subprocess.run([
        sys.executable,
        "-m",
        "uvicorn",
        "main:app",
        "--reload"
    ])


if __name__ == "__main__":
    check_venv()
    time.sleep(0.5)
    run_backend()
