from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Optional, Any

app = FastAPI(
    title="SecretFlow PIT Task API",
    description="API for launching, querying, stopping, and receiving PET task callbacks",
    version="1.0.0"
)

# ----------------------------------
# 数据模型定义
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
    capacity: int = Field(..., description="Max concurrency number of executing tasks")
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
# 内存模拟任务状态
# ----------------------------------
TASK_CAPACITY = 3
running_tasks = []
task_results = {}  # 存储回调结果


# ----------------------------------
# 1️⃣ 启动任务接口
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

        running_tasks.append(request.taskId)
        print(f"Task started: {request.taskId}")

        return APIResponse(
            code="00",
            message="query created successfully",
            data={}
        )

    except Exception as e:
        return APIResponse(
            code="02",
            message=f"External server error, server message: {str(e)}",
            data={}
        )


# ----------------------------------
# 2️⃣ 查询系统状态接口
# ----------------------------------
@app.get("/SecretFlow/api/v1/status/", response_model=QueryStatusResponse)
async def query_status():
    try:
        capacity = TASK_CAPACITY
        available = max(capacity - len(running_tasks), 0)
        return QueryStatusResponse(
            capacity=capacity,
            availableTaskNum=available,
            runningTasks=running_tasks
        )
    except Exception:
        return QueryStatusResponse(
            capacity=0,
            availableTaskNum=0,
            runningTasks=[]
        )


# ----------------------------------
# 3️⃣ 停止任务接口
# ----------------------------------
@app.delete("/SecretFlow/api/v1/{task_id}", response_model=APIResponse)
async def stop_task(task_id: str):
    try:
        if task_id not in running_tasks:
            return APIResponse(
                code="01",
                message=f"failed to stop the task {task_id}. Cause: task not found",
                data={}
            )

        running_tasks.remove(task_id)
        print(f"Task stopped: {task_id}")

        return APIResponse(
            code="00",
            message="success",
            data={}
        )

    except Exception as e:
        return APIResponse(
            code="01",
            message=f"failed to stop the task {task_id}. Cause: {str(e)}",
            data={}
        )


# ----------------------------------
# 4️⃣ PET Task Callback 接口
# ----------------------------------
@app.post("/SecretFlow/api/v1/callback", response_model=APIResponse)
async def pet_task_callback(request: PETTaskCallbackRequest):
    """
    Receive PET Task callback results from PET Platform
    """
    try:
        # 模拟记录结果
        task_results[request.taskId] = {
            "status": request.taskResultStatusCode,
            "message": request.message,
            "totalBlocks": request.totalBlockNums,
            "currentBlock": request.currentBlockNum,
            "recordCount": request.currentRecordNums,
            "results": request.resultValueList
        }

        # 如果任务已完成则移出运行列表
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
