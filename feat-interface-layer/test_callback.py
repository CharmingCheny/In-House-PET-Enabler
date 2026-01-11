import requests
import json
import time
import sys

BASE_URL = "http://127.0.0.1:8000/SecretFlow/api/v1"
TASK_ID = "callback-test-task"

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

    # 2. Poll status until finished
    max_retries = 30
    for i in range(max_retries):
        print(f"⏳ Waiting for task to complete ({i+1}/{max_retries})...")
        time.sleep(2)
        status_resp = query_task_status()
        
        if not status_resp:
            continue
            
        data = status_resp.get("data", {})
        status = data.get("status")
        message = data.get("message")
        
        if status == "success":
            print(f"✅ Task finished successfully! Message: {message}")
            # Check if callback was processed (implied by success message in our modified code)
            if "Callback finished" in message or "Task and Callback finished" in message:
                print("✅ Callback logic executed.")
            break
        elif status == "failed" or status == "callback_failed":
            print(f"❌ Task failed. Status: {status}, Message: {message}")
            break
        elif status_resp.get("message") == "Task finished":
             # Sometimes it might jump to finished state in task_results
             print(f"✅ Task finished. Data: {data}")
             break

if __name__ == "__main__":
    main()
