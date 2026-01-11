import requests
import json
import time
import sys

BASE_URL = "http://127.0.0.1:8000/SecretFlow/api/v1"
TASK_ID = "stop-test-task"

def launch_task():
    url = f"{BASE_URL}/pit-tasks"
    payload = {
        "taskId": TASK_ID,
        "requesterDataObjectId": "100",
        "collaboratorDataObjectId": "200",
        "collaboratorFields": ["emp_no", "name", "salary"],
        "algorithmSource": "Secretflow",
        "algorithmProtocol": "ECDM-PSI",
        "algorithmVersion": "V1.0",
        "logicFormula": "emp_no&emp_no",
        "valueFields": ["salary"]
    }
    print(f"🟢 Launching task {TASK_ID}...")
    try:
        res = requests.post(url, json=payload)
        print(f"Launch response: {res.status_code} {res.json()}")
    except Exception as e:
        print(f"Failed to launch task: {e}")
        sys.exit(1)

def stop_task():
    url = f"{BASE_URL}/{TASK_ID}"
    print(f"🛑 Stopping task {TASK_ID}...")
    try:
        res = requests.delete(url)
        print(f"Stop response: {res.status_code} {res.json()}")
    except Exception as e:
        print(f"Failed to stop task: {e}")

def query_task_status():
    url = f"{BASE_URL}/task/{TASK_ID}"
    print(f"🔍 Querying task status for {TASK_ID}...")
    try:
        res = requests.get(url)
        print(f"Status response: {res.status_code} {res.json()}")
        return res.json()
    except Exception as e:
        print(f"Failed to query status: {e}")
        return None

def main():
    # 1. Launch the task
    launch_task()

    # 2. Wait a bit to let it start running (e.g., entering preprocessing or PSI phase)
    print("⏳ Waiting for 3 seconds to let the task run...")
    time.sleep(3)

    # 3. Check status (should be running)
    status = query_task_status()
    if status and status.get("message") == "Task is running":
        print("✅ Task is currently running as expected.")
    else:
        print("⚠️ Task might not be running or finished too quickly.")

    # 4. Stop the task
    stop_task()

    # 5. Wait a moment for the server to process the stop
    time.sleep(1)

    # 6. Check status again (should be stopped or finished)
    status = query_task_status()
    data = status.get("data", {})
    if data.get("status") == "stopped":
        print("✅ Test Passed: Task was successfully stopped.")
    else:
        print(f"❌ Test Failed: Task status is {data.get('status')}, expected 'stopped'.")

if __name__ == "__main__":
    main()
