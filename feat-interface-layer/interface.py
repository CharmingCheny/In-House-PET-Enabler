from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Optional, Any
import subprocess
import threading
import uuid
import os
import signal
import requests
import socket

app = FastAPI(
    title="SecretFlow PIT Task API",
    description="API for launching, querying, stopping, and receiving PET task callbacks",
    version="1.0.0"
)

# ----------------------------------
# Data Model Definitions
# ----------------------------------
class LaunchTaskRequest(BaseModel):
    taskId: str
    requesterDataObjectId: str
    collaboratorDataObjectId: str
    collaboratorFields: List[str]
    algorithmSource: str
    algorithmProtocol: str
    algorithmVersion: str
    logicFormula: str
    valueFields: Optional[List[str]] = None


class APIResponse(BaseModel):
    code: str
    message: str
    data: dict


class QueryStatusResponse(BaseModel):
    capacity: int = Field(..., description="Maximum number of concurrently executing tasks")
    availableTaskNum: int = Field(..., description="Remaining available task slots")
    runningTasks: List[str] = Field(..., description="Currently running task IDs")


class ResultValue(BaseModel):
    field1: Optional[str] = None
    resultFlag: bool


class PETTaskCallbackRequest(BaseModel):
    taskId: str
    taskResultStatusCode: str
    message: str
    requesterDataObjectId: str
    collaboratorDataObjectId: str
    collaboratorFields: List[str]
    algorithmSource: str
    algorithmProtocol: str
    algorithmVersion: str
    logicFormula: str
    valueFields: List[str]
    resultValueList: List[Any]
    totalBlockNums: int
    currentBlockNum: int
    currentRecordNums: int


# ----------------------------------
# In-memory Task State Simulation
# ----------------------------------
TASK_CAPACITY = 3

# 运行中的任务信息: {task_id: {"process": Popen, "status": str, "message": str}}
running_tasks: dict[str, dict[str, Any]] = {}

# 历史/完成任务结果: {task_id: {"status": str, "message": str}}
task_results: dict[str, dict[str, Any]] = {}

BOB_IP = os.getenv("BOB_HOST", "127.0.0.1")
BOB_PORT = int(os.getenv("BOB_PORT", "8002"))

def _get_current_party():
    """Determine current party based on env var or config file existence."""
    # Priority 1: Env Var
    env_party = os.getenv("PARTY")
    if env_party:
        return env_party.lower()

    # Priority 2: File existence
    base_dir = "/export/coding/secretflow_core"
    if os.path.exists(os.path.join(base_dir, "cluster_alice.yaml")):
        return "alice"
    elif os.path.exists(os.path.join(base_dir, "cluster_bob.yaml")):
        return "bob"
    return "unknown"

def _build_paths(request: LaunchTaskRequest, party: str):
    """Construct paths based on party."""
    base_dir = "/export/coding/secretflow_core"
    
    if party == "alice":
        cluster_yaml = os.path.join(base_dir, "cluster_alice.yaml")
    else:
        cluster_yaml = os.path.join(base_dir, "cluster_bob.yaml")

    # Data paths
    alice_in = os.path.join(base_dir, "data", "alice_table.csv")
    bob_in = os.path.join(base_dir, "data", f"bob_psi_{request.collaboratorDataObjectId}.csv")

    # Output path: Save in data folder as requested
    alice_out = os.path.join(
        base_dir,
        "data",
        f"psi_result_{request.taskId}.csv",
    )
    bob_out = os.path.join(
        base_dir,
        "data",
        f"psi_result_{request.taskId}_bob.csv",
    )

    join_key = request.collaboratorFields[0] if request.collaboratorFields else "id"

    return cluster_yaml, alice_in, bob_in, alice_out, bob_out, join_key


def _start_task_execution(task_id: str, request: LaunchTaskRequest):
    """启动任务执行流程：数据预处理 -> PSI"""
    from pathlib import Path
    import sys

    base_dir = "/export/coding/secretflow_core"
    preprocess_script = "/export/coding/data_preprocess/preprocess.py"
    run_psi_py = os.path.join(base_dir, "run_psi.py")
    
    party = _get_current_party()
    print(f"[{task_id}] Current party identified as: {party}")

    (
        cluster_yaml,
        alice_in,
        bob_in,
        alice_out,
        bob_out,
        join_key,
    ) = _build_paths(request, party)

    # Only create directories for the current party's data
    if party == "alice":
        Path(os.path.dirname(alice_in)).mkdir(parents=True, exist_ok=True)
        Path(os.path.dirname(alice_out)).mkdir(parents=True, exist_ok=True)
    elif party == "bob":
        Path(os.path.dirname(bob_in)).mkdir(parents=True, exist_ok=True)
        Path(os.path.dirname(bob_out)).mkdir(parents=True, exist_ok=True)

    # Initialize task status
    running_tasks[task_id] = {
        "process": None,
        "status": "starting",
        "message": "Task initialized",
    }

    def _run_sequence():
        try:
            fields_str = ",".join(request.collaboratorFields)
            
            # 1. Preprocess (Role-based)
            if party == "alice":
                # Alice Preprocess
                cmd_alice = [
                    sys.executable, "-u", preprocess_script,
                    "--data_object_id", request.requesterDataObjectId,
                    "--fields", fields_str,
                    "--csv_path", alice_in
                ]
                print(f"[{task_id}] Starting Alice preprocess: {' '.join(cmd_alice)}")
                proc_alice = subprocess.Popen(
                    cmd_alice, cwd=base_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
                )
                running_tasks[task_id]["process"] = proc_alice
                running_tasks[task_id]["status"] = "preprocessing_alice"
                running_tasks[task_id]["message"] = "Preprocessing Alice data"
                
                for line in proc_alice.stdout:
                    print(f"[Preprocess-Alice-{task_id}] {line.rstrip()}")
                
                rc_alice = proc_alice.wait()
                if rc_alice != 0:
                    raise Exception(f"Alice preprocessing failed with code {rc_alice}")

                # Trigger Bob
                try:
                    bob_url = f"http://{BOB_IP}:{BOB_PORT}/SecretFlow/api/v1/pit-tasks"
                    print(f"[{task_id}] Triggering Bob at {bob_url}...")
                    # Use a short timeout to avoid blocking if Bob is offline
                    requests.post(bob_url, json=request.dict(), timeout=5)
                    print(f"[{task_id}] Trigger sent to Bob successfully.")
                except Exception as e:
                    print(f"[{task_id}] Warning: Failed to trigger Bob: {e}")
                    # We continue, assuming Bob might be started manually or this is a test

            elif party == "bob":
                # Bob Preprocess
                cmd_bob = [
                    sys.executable, "-u", preprocess_script,
                    "--data_object_id", request.collaboratorDataObjectId,
                    "--fields", fields_str,
                    "--csv_path", bob_in
                ]
                print(f"[{task_id}] Starting Bob preprocess: {' '.join(cmd_bob)}")
                proc_bob = subprocess.Popen(
                    cmd_bob, cwd=base_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
                )
                running_tasks[task_id]["process"] = proc_bob
                running_tasks[task_id]["status"] = "preprocessing_bob"
                running_tasks[task_id]["message"] = "Preprocessing Bob data"

                for line in proc_bob.stdout:
                    print(f"[Preprocess-Bob-{task_id}] {line.rstrip()}")

                rc_bob = proc_bob.wait()
                if rc_bob != 0:
                    raise Exception(f"Bob preprocessing failed with code {rc_bob}")

            # 3. Run PSI
            cmd_psi = [
                sys.executable, "-u",
                run_psi_py,
                cluster_yaml,
                alice_in,
                bob_in,
                alice_out,
                bob_out,
                join_key,
            ]

            print(f"[{task_id}] Starting PSI: {' '.join(cmd_psi)}")
            proc_psi = subprocess.Popen(
                cmd_psi, cwd=base_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            running_tasks[task_id]["process"] = proc_psi
            running_tasks[task_id]["status"] = "running_psi"
            running_tasks[task_id]["message"] = "PSI task running"

            for line in proc_psi.stdout:
                print(f"[PSI-{task_id}] {line.rstrip()}")

            rc_psi = proc_psi.wait()
            status = "success" if rc_psi == 0 else "failed"
            msg = f"Task finished with code {rc_psi}"

            # 4. Post Result (Callback) - Only for Alice (Requester)
            if status == "success" and party == "alice":
                post_result_script = os.path.join(base_dir, "post_result.py")
                callback_url = f"http://127.0.0.1:8000/SecretFlow/api/v1/callback"
                
                cmd_callback = [
                    sys.executable, "-u", post_result_script,
                    "--result_file", alice_out,
                    "--task_id", task_id,
                    "--callback_url", callback_url,
                    "--join_key", join_key,
                    "--req_data_id", request.requesterDataObjectId,
                    "--col_data_id", request.collaboratorDataObjectId
                ]
                
                print(f"[{task_id}] Starting Callback: {' '.join(cmd_callback)}")
                proc_callback = subprocess.Popen(
                    cmd_callback, cwd=base_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
                )
                running_tasks[task_id]["process"] = proc_callback
                running_tasks[task_id]["status"] = "callback_processing"
                running_tasks[task_id]["message"] = "Processing and sending results"

                for line in proc_callback.stdout:
                    print(f"[Callback-{task_id}] {line.rstrip()}")
                
                rc_callback = proc_callback.wait()
                if rc_callback != 0:
                    status = "callback_failed"
                    msg = f"Callback failed with code {rc_callback}"
                else:
                    msg = "Task and Callback finished successfully"

            running_tasks.pop(task_id, None)
            task_results[task_id] = {"status": status, "message": msg}
            print(f"[{task_id}] Finished: {status}")

        except Exception as e:
            print(f"[{task_id}] Error: {e}")
            running_tasks.pop(task_id, None)
            task_results[task_id] = {"status": "failed", "message": str(e)}

    t = threading.Thread(target=_run_sequence, daemon=True)
    t.start()


# ----------------------------------
# 1️⃣ Launch Task API
# ----------------------------------
@app.post("/SecretFlow/api/v1/pit-tasks", response_model=APIResponse)
async def launch_task(request: LaunchTaskRequest):
    try:
        if len(running_tasks) >= TASK_CAPACITY:
            return APIResponse(
                code="01",
                message="Failed to create query. Cause: Task capacity reached",
                data={}
            )
        task_id = request.taskId or str(uuid.uuid4())

        if task_id in running_tasks:
            return APIResponse(
                code="01",
                message=f"Task {task_id} is already running",
                data={},
            )

        _start_task_execution(task_id, request)
        print(f"Task started: {task_id}")

        return APIResponse(
            code="00",
            message="Query created successfully",
            data={"taskId": task_id}
        )

    except Exception as e:
        return APIResponse(
            code="02",
            message=f"External server error, server message: {str(e)}",
            data={}
        )


# ----------------------------------
# 2️⃣ Query System Status API
# ----------------------------------
@app.get("/SecretFlow/api/v1/status/", response_model=QueryStatusResponse)
async def query_status():
    try:
        capacity = TASK_CAPACITY
        available = max(capacity - len(running_tasks), 0)
        running_ids = list(running_tasks.keys())
        return QueryStatusResponse(
            capacity=capacity,
            availableTaskNum=available,
            runningTasks=running_ids
        )
    except Exception:
        return QueryStatusResponse(
            capacity=0,
            availableTaskNum=0,
            runningTasks=[]
        )


# ----------------------------------
# 2.5 Query Task Result API (New)
# ----------------------------------
@app.get("/SecretFlow/api/v1/task/{task_id}", response_model=APIResponse)
async def query_task_result(task_id: str):
    # Check running tasks
    if task_id in running_tasks:
        info = running_tasks[task_id]
        return APIResponse(
            code="00",
            message="Task is running",
            data={"status": info["status"], "message": info["message"]}
        )
    
    # Check finished tasks
    if task_id in task_results:
        res = task_results[task_id]
        return APIResponse(
            code="00",
            message="Task finished",
            data=res
        )

    return APIResponse(
        code="01",
        message="Task not found",
        data={}
    )


# ----------------------------------
# 3️⃣ Stop Task API
# ----------------------------------
@app.delete("/SecretFlow/api/v1/{task_id}", response_model=APIResponse)
async def stop_task(task_id: str):
    try:
        info = running_tasks.get(task_id)
        if not info:
            return APIResponse(
                code="01",
                message=f"Failed to stop the task {task_id}. Cause: Task not found",
                data={}
            )
        proc: subprocess.Popen = info["process"]
        try:
            if proc.poll() is None:
                os.kill(proc.pid, signal.SIGTERM)
        except Exception as e:
            return APIResponse(
                code="01",
                message=f"Failed to stop the task {task_id}. Cause: {str(e)}",
                data={},
            )

        running_tasks.pop(task_id, None)
        task_results[task_id] = {
            "status": "stopped",
            "message": "Task stopped by user",
        }
        print(f"Task stopped: {task_id}")

        return APIResponse(
            code="00",
            message="Success",
            data={}
        )

    except Exception as e:
        return APIResponse(
            code="01",
            message=f"Failed to stop the task {task_id}. Cause: {str(e)}",
            data={}
        )


# ----------------------------------
# 4️⃣ PET Task Callback API
# ----------------------------------
@app.post("/SecretFlow/api/v1/callback", response_model=APIResponse)
async def pet_task_callback(request: PETTaskCallbackRequest):
    """
    Receive PET Task callback results from PET Platform
    """
    try:
        # Simulate storing results
        task_results[request.taskId] = {
            "status": request.taskResultStatusCode,
            "message": request.message,
            "totalBlocks": request.totalBlockNums,
            "currentBlock": request.currentBlockNum,
            "recordCount": request.currentRecordNums,
            "results": request.resultValueList
        }

        # Remove from running list if task completed successfully
        if request.taskId in running_tasks and request.taskResultStatusCode == "00":
            running_tasks.remove(request.taskId)

        print(f"Callback received for task {request.taskId}: {request.message}")

        return APIResponse(
            code="00",
            message="Callback processed successfully",
            data={}
        )

    except Exception as e:
        return APIResponse(
            code="01",
            message=f"Failed to process callback for {request.taskId}. Cause: {str(e)}",
            data={}
        )
