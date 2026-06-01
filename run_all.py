import subprocess
import time
import sys
import os
import shutil

def print_banner():
    """Displays a simple ASCII banner for the system."""
    print("=" * 60)
    print("   🚀 AI/ML TRADING PREDICTION SYSTEM - STARTUP CONTROL")
    print("=" * 60)
    print(f"Current Directory: {os.getcwd()}")
    print(f"Python Version: {sys.version.split()[0]}")
    print("-" * 60)

def run_system():
    print_banner()

    # --- STEP 1: PRE-FLIGHT CHECKS (Directories & Models) ---
    backend_dir = os.path.join(os.getcwd(), "backend")
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    model_path = os.path.join(backend_dir, "models", "saved_model.h5")
    scaler_path = os.path.join(backend_dir, "models", "scaler.pkl")

    # Ensure the frontend directory exists before we even try to run it
    if not os.path.exists(frontend_dir):
        print(f"❌ ERROR: Frontend directory not found at {frontend_dir}")
        print("Please ensure you are running this script from the project root.")
        return

    # Ensure the backend directory exists
    if not os.path.exists(backend_dir):
        print(f"❌ ERROR: Backend directory not found at {backend_dir}")
        return

    print("🔍 Checking model artifacts...")
    
    # Check if model or scaler exists and are not tiny/corrupted files
    model_missing = not os.path.exists(model_path) or os.path.getsize(model_path) < 1000
    scaler_missing = not os.path.exists(scaler_path) or os.path.getsize(scaler_path) < 100

    if model_missing or scaler_missing:
        print(f"⚠️  {'Model' if model_missing else 'Scaler'} file is missing or invalid. Starting training process...")
        try:
            # Run training as a package module from the root
            subprocess.run([sys.executable, "-m", "backend.models.train_model"], check=True)
            print("✅ Training completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error during training: {e}")
            return

    # --- STEP 2: LAUNCH BACKEND (FastAPI) ---
    print("\n📡 Launching Backend Server...")
    print("   URL: http://127.0.0.1:8000")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.app:app", "--host", "127.0.0.1", "--port", "8000", "--log-level", "info"]
    )

    print("⏳ Waiting for backend to initialize...")
    time.sleep(4)  # Increased wait time for stability

    # --- STEP 3: LAUNCH FRONTEND (React) ---
    print("\n💻 Launching Frontend Dashboard...")
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    
    # Check if npm is installed
    if not shutil.which(npm_cmd):
        print(f"❌ ERROR: '{npm_cmd}' not found. Please install Node.js from https://nodejs.org/")
        backend_process.terminate()
        return

    frontend_process = subprocess.Popen(
        [npm_cmd, "start"],
        cwd=os.path.join(os.getcwd(), "frontend"),
        shell=(os.name == "nt")
    )

    try:
        # Keep the script alive while processes are running
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down system...")
        backend_process.terminate()
        frontend_process.terminate()

if __name__ == "__main__":
    run_system()