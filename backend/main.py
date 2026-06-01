import uvicorn
import os
import sys

# Add the current directory to sys.path to handle imports correctly when running main.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app import app

if __name__ == "__main__":
    # Using the string import "backend.main:app" allows the reload flag to work properly
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)