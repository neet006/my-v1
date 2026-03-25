"""
run.py — Quick launcher for A.M.A.T.S. Web Server.
Run from project root: python run.py
"""
import subprocess, sys, os

if __name__ == "__main__":
    script = os.path.join(os.path.dirname(__file__), "backend", "app.py")
    subprocess.run([sys.executable, script])
