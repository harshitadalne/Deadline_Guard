"""
Run script to start Deadline Guardian application.
This script starts both the FastAPI backend and Streamlit frontend.
"""
import subprocess
import sys
import os
from pathlib import Path


def run_backend():
    """Start the FastAPI backend server."""
    print("Starting FastAPI backend...")
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])


def run_frontend():
    """Start the Streamlit frontend."""
    print("Starting Streamlit frontend...")
    frontend_dir = Path(__file__).parent / "frontend"
    os.chdir(frontend_dir)
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501"])


def main():
    """Main entry point."""
    print("🛡️ Deadline Guardian")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "backend":
            run_backend()
        elif sys.argv[1] == "frontend":
            run_frontend()
        elif sys.argv[1] == "seed":
            print("Seeding database...")
            from backend.database.seed import seed_database
            seed_database()
        else:
            print("Usage: python run.py [backend|frontend|seed]")
            print("  backend  - Start FastAPI backend server")
            print("  frontend - Start Streamlit frontend")
            print("  seed     - Seed database with demo data")
    else:
        print("Please specify what to run:")
        print("  python run.py backend   - Start FastAPI backend server")
        print("  python run.py frontend  - Start Streamlit frontend")
        print("  python run.py seed      - Seed database with demo data")
        print("\nFor development, run backend and frontend in separate terminals.")


if __name__ == "__main__":
    main()
