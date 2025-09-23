#!/usr/bin/env python3
"""
launcher script for the premier league player role discovery app.

this script provides a convenient way to launch the streamlit app and
run validation tests.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

def parse_args():
    """parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Premier League Player Role Discovery App Launcher"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run validation tests before launching the app"
    )
    parser.add_argument(
        "--test-only",
        action="store_true",
        help="Run validation tests without launching the app"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="Port to run the Streamlit app on (default: 8501)"
    )
    return parser.parse_args()

def run_tests():
    """run app validation tests."""
    print("Running validation tests...")
    test_script = Path(__file__).parent / "app" / "utils" / "test_app.py"
    
    if not test_script.exists():
        print(f"❌ Test script not found: {test_script}")
        return False
    
    result = subprocess.run([sys.executable, str(test_script)], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ All tests passed!")
        print(result.stdout)
        return True
    else:
        print("❌ Tests failed!")
        print(result.stdout)
        print(result.stderr)
        return False

def launch_app(port):
    """launch the streamlit app."""
    app_path = Path(__file__).parent / "app" / "Home.py"
    
    if not app_path.exists():
        print(f"❌ App not found: {app_path}")
        return False
    
    print(f"🚀 Launching Streamlit app on port {port}...")
    subprocess.run(["streamlit", "run", str(app_path), "--server.port", str(port)])
    return True

def main():
    """main function."""
    args = parse_args()
    
    if args.test or args.test_only:
        tests_passed = run_tests()
        if not tests_passed and not args.test_only:
            print("❌ Tests failed. Fix issues before launching the app.")
            sys.exit(1)
        
        if args.test_only:
            sys.exit(0 if tests_passed else 1)
    
    launch_app(args.port)

if __name__ == "__main__":
    main()
