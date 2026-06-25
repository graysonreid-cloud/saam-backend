import sys
import os
import time


# Ensure project root is on PYTHONPATH
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# IMPORTANT: import models AFTER sys.path is set
import db.db_models

from db.database import init_db
import uvicorn


def run_backend():
    """
    Starts the SAAM backend.
    Assumes the user has already activated the correct virtual environment.
    No venv path checks are performed.
    """
    print("Starting SAAM backend with command: uvicorn main:app --reload")
    print("*** Don't forget to start ngrok with: start_webhook.py ***")

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    # Initialize DB
    try:
        init_db()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Database initialization failed: {e}")

    time.sleep(0.5)

    # Start backend
    run_backend()
