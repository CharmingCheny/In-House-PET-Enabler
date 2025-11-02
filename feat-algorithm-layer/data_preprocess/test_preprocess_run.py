#!/usr/bin/env python3
import time, requests, os, sys

PREPROCESS_URL = os.getenv("PREPROCESS_URL", "http://127.0.0.1:8000/preprocess/extract")
CSV_PATH = os.getenv("TEST_CSV_PATH", "/export/coding/data_preprocess/output/employee.csv")

payload = {
    "dataObjectId": "employee_task_1",
    "fields": ["emp_no", "name", "department", "email", "salary", "hire_date"],
    "csvPath": os.path.abspath(CSV_PATH)
}

print("POST", PREPROCESS_URL)
print("payload:", payload)
try:
    r = requests.post(PREPROCESS_URL, json=payload, timeout=30)
except Exception as e:
    print("Request error:", e); sys.exit(1)

print("Status:", r.status_code)
try:
    print("Body:", r.json())
except:
    print("Body text:", r.text)

if r.status_code != 200:
    print("Request failed"); sys.exit(2)

out = payload["csvPath"]
for i in range(20):
    if os.path.exists(out):
        break
    time.sleep(0.5)
if not os.path.exists(out):
    print("CSV not found:", out); sys.exit(3)

print("CSV found:", out)
with open(out, "r", encoding="utf-8") as f:
    print(f.read())
