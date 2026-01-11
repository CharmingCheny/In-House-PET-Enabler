#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import signal

# This script now tests the CLI mode of preprocess.py, matching the system architecture
PREPROCESS_SCRIPT = "/export/coding/data_preprocess/preprocess.py"
CSV_PATH = "/export/coding/secretflow_core/data/test_extract.csv"

# Ensure output dir exists
os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)

# 1. Start Mock DTM (Required for metadata)
print("Starting Mock DTM...")
dtm_process = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "data_preprocess.mock_dtm:app", "--host", "127.0.0.1", "--port", "8001"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
time.sleep(2) # Wait for startup

try:
    print(f"Testing Preprocess CLI...")
    # Enable Mock DB Failover so we don't need a real DB
    env = os.environ.copy()
    env["MOCK_DB_FAILOVER"] = "true"
    
    cmd = [
        sys.executable, PREPROCESS_SCRIPT,
        "--data_object_id", "test_obj_1",
        "--fields", "emp_no,name,salary",
        "--csv_path", CSV_PATH
    ]

    print(f"Running command: {' '.join(cmd)}")

    # Run the command
    result = subprocess.run(cmd, check=True, capture_output=True, text=True, env=env)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    
    if os.path.exists(CSV_PATH):
        print(f"✅ Success! CSV found at: {CSV_PATH}")
        print("Content preview:")
        with open(CSV_PATH, "r") as f:
            print(f.read())
    else:
        print(f"❌ Failed! CSV not found at: {CSV_PATH}")
        sys.exit(1)

except subprocess.CalledProcessError as e:
    print(f"❌ Execution failed with code {e.returncode}")
    print("STDOUT:", e.stdout)
    print("STDERR:", e.stderr)
    sys.exit(1)
finally:
    # Cleanup DTM
    print("Stopping Mock DTM...")
    dtm_process.terminate()
    dtm_process.wait()
