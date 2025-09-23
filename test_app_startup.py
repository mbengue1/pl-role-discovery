#!/usr/bin/env python3
"""
test script to verify the streamlit app can start properly.
"""

import sys
import subprocess
import time
from pathlib import Path

def test_app_startup():
    """test that the streamlit app can start without errors."""
    print("🧪 Testing Streamlit app startup...")
    
    # change to project directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    try:
        # start streamlit in a subprocess
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "app/Home.py",
            "--server.port", "8502",  # use different port
            "--server.headless", "true"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # wait a few seconds for startup
        time.sleep(5)
        
        # check if process is still running
        if process.poll() is None:
            print("✅ Streamlit app started successfully")
            process.terminate()
            process.wait()
            return True
        else:
            # get error output
            stdout, stderr = process.communicate()
            print(f"❌ Streamlit app failed to start")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting Streamlit app: {e}")
        return False

if __name__ == "__main__":
    import os
    success = test_app_startup()
    sys.exit(0 if success else 1)
