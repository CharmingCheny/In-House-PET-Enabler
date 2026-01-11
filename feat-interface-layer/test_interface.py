import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/SecretFlow/api/v1"
TASK_ID = "example-task-id"

# -------------------------------
# 1️⃣ Launch
# -------------------------------
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
    print("🟢 Launching task...")
    res = requests.post(url, json=payload)
    print(res.status_code, res.json(), "\n")


# -------------------------------
# 2️⃣ Status
# -------------------------------
def query_status():
    url = f"{BASE_URL}/status/"
    print("🔵 Querying status...")
    res = requests.get(url)
    print(res.status_code, res.json(), "\n")


# -------------------------------
# 3️⃣ Callback
# -------------------------------
def pet_callback():
    url = f"{BASE_URL}/callback"
    payload = {
        "taskId": TASK_ID,
        "taskResultStatusCode": "00",
        "message": "success",
        "requesterDataObjectId": "data-object-1",
        "collaboratorDataObjectId": "data-object-2",
        "collaboratorFields": ["field1", "field2"],
        "algorithmSource": "SecretFlow",
        "algorithmProtocol": "ECDN-PSI",
        "algorithmVersion": "V1.0",
        "logicFormula": "field1&field2",
        "valueFields": ["field1", "field2"],
        "resultValueList": [
            {"field1": "value1", "resultFlag": True},
            {"field1": "value2", "resultFlag": False}
        ],
        "totalBlockNums": 20,
        "currentBlockNum": 10,
        "currentRecordNums": 100
    }
    print("🟡 Sending PET callback...")
    res = requests.post(url, json=payload)
    print(res.status_code, res.json(), "\n")


# -------------------------------
# 4️⃣ Stop
# -------------------------------
def stop_task():
    url = f"{BASE_URL}/{TASK_ID}"
    print("🔴 Stopping task...")
    res = requests.delete(url)
    print(res.status_code, res.json(), "\n")



if __name__ == "__main__":
    print("🚀 Starting automated API test...\n")
    launch_task()
    
    # Wait for task to progress
    print("🔵 Polling task status...")
    for _ in range(60):
        time.sleep(2)
        # Query system status
        res = requests.get(f"{BASE_URL}/status/")
        status_data = res.json()
        print(f"System Status: {status_data}")
        
        # Query specific task result
        res_task = requests.get(f"{BASE_URL}/task/{TASK_ID}")
        task_data = res_task.json()
        print(f"Task Status: {task_data}")
        
        if task_data['message'] == "Task finished":
            print("✅ Task completed!")
            break

    # stop_task() # Optional: stop if running
    time.sleep(1)
    query_status()
    print("✅ Test completed.")
