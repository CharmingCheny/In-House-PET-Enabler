# PrivacyGuard - Internal Data Privacy Protection Tool

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Security](https://img.shields.io/badge/Security-PII%20Compliant-red)

A comprehensive privacy-preserving tool that automatically detects, redacts, and encrypts sensitive information from documents and data streams.

## 📋 Table of Contents
- [Overview](#-overview)
- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Usage Examples](#-usage-examples)
- [API Documentation](#-api-documentation)
- [Security](#-security)
- [Contributing](#-contributing)
- [License](#-license)

## 🛡️ Overview

The **Internal Privacy-Enhancing Computation Framework** is an enterprise-grade solution custom-built for financial institutions. Based on the open-source SecretFlow platform, it integrates advanced cryptographic protocols to achieve secure and efficient cross-institutional sensitive data collaboration and joint analysis without exposing raw data. This framework is committed to ensuring data sovereignty, regulatory compliance, and laying a solid foundation for future privacy-preserving financial applications.
Key Capabilities:
- **Secure Collaboration Foundation:** At its core, it integrates Privacy-Enhancing Technologies (PETs) such as Secure Multi-Party Computation (MPC) and Private Set Intersection (PSI). It supports joint computation on private inputs from multiple parties, suitable for scenarios like federated anti-fraud and joint risk indicator calculation.
- **Modular Protocol Support:** It features a designed and implemented configurable PSI execution framework, supporting various protocol variants (e.g., ECDH, KKRT, RR22). This allows for flexible selection based on application requirements, balancing speed, scalability, and privacy guarantees.
- **Financial-Grade Performance and Scalability:** Comprehensive performance evaluation was conducted on simulated financial datasets. It is proven to deliver scalable performance and operational stability with up to $10^6$ records and in 1:1000 asymmetric configurations.
- **Unified Interface and Task Management:** Utilizing the FastAPI framework, it provides a unified interface layer that abstracts underlying cryptographic complexity, supporting the full lifecycle management of PSI tasks, including status queries and secure termination.


## ✨ Features

### 🔐 Secure Multi-Party Collaboration
- **Privacy-Preserving Set Intersection (PSI)** powered by **SecretFlow SPU**
- **Dual-Role Execution**：Initiator & Collaborator workflow separation
- **End-to-End Confidentiality**：No raw data leaves local storage
- **Metadata-Guided Computation**：Only required columns are exposed

#### Supported PSI Protocols
- **RR22 (Curve25519)** — High performance & scalable  
- **KKRT** — Efficient OT-based PSI for large datasets  
- **ECDH** — Broad compatibility fallback

### ⚙️ Flexible & Scalable Execution
- **Dynamic Resource Allocation**：Port & runtime isolation based on Task ID
- **Parallel Multi-Task Support**：Shared cluster, conflict-free execution
- **Protocol Agility**：Automatic protocol selection based on workload

### 📦 Multi-Source Data Integration
- **Metadata-Driven Data Loading** via Data Trust Manager (DTM)
- Supports industry databases:
  - PostgreSQL
  - MySQL
- **Standardized export** to SecretFlow-compatible CSV

### 📡 API-Level Task Orchestration
- **Launch PSI Task**
- **Query Task Status**
- **Callback Notification**
- **Forced Task Stop**
- Full **lifecycle visibility** for enterprise workflows


## 🚀 Installation

### Prerequisites
- Python 3.10.18
- 3.8GB RAM
- 20GB free disk space

### Quick Installation
```bash
# Clone the repository (internal network only)
cd /export/coding/secretflow_core
git clone https://github.com/CharmingCheny/In-House-PET-Enabler.git

# Create and activate virtual environment
conda create -n sf python=3.10
conda activate sf

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import privacy_guard; print('Installation successful!')"
```

### Docker Installation
```bash
# Pull from internal registry

# Run container
```

## ⚡ Quick Start

### Command Line Interface
```bash
# Basic file redaction
python -m uvicorn interface:app --reload --host 0.0.0.0 --port 8000 --workers 1
```

### Python API
```python

```

## ⚙️ Configuration

### Basic Configuration File


### Environment Variables
```bash

```

## 💻 Usage Examples

### Example 1: Launch a PIT Task
```python
import requests

url = "http://localhost:8000/SecretFlow/api/v1/pit-tasks"

payload = {
    "taskId": "task_001",
    "requesterDataObjectId": "requester_ds_01",
    "collaboratorDataObjectId": "collaborator_ds_01",
    "collaboratorFields": ["user_id", "email"],
    "algorithmSource": "SecretFlow",
    "algorithmProtocol": "PSI",
    "algorithmVersion": "v1.0",
    "logicFormula": "AND",
    "valueFields": ["score"]
}

response = requests.post(url, json=payload)
result = response.json()

print(result["message"])
```

### Example 2: Query System Status
```python
import requests

url = "http://localhost:8000/SecretFlow/api/v1/status/"

response = requests.get(url)
status = response.json()

print(f"Capacity: {status['capacity']}")
print(f"Available Slots: {status['availableTaskNum']}")
print(f"Running Tasks: {status['runningTasks']}")
```

### Example 3: Stop a Running Task
```python
import requests

task_id = "task_001"
url = f"http://localhost:8000/SecretFlow/api/v1/{task_id}"

response = requests.delete(url)
result = response.json()

print(result["message"])
```


### Example 4: PET Task Result Callback
```python
import requests

url = "http://localhost:8000/SecretFlow/api/v1/callback"

payload = {
    "taskId": "task_001",
    "taskResultStatusCode": "00",
    "message": "Task executed successfully",
    "requesterDataObjectId": "requester_ds_01",
    "collaboratorDataObjectId": "collaborator_ds_01",
    "collaboratorFields": ["user_id", "email"],
    "algorithmSource": "SecretFlow",
    "algorithmProtocol": "PSI",
    "algorithmVersion": "v1.0",
    "logicFormula": "AND",
    "valueFields": ["score"],
    "resultValueList": [
        {"user_id": "u001", "resultFlag": True},
        {"user_id": "u002", "resultFlag": False}
    ],
    "totalBlockNums": 1,
    "currentBlockNum": 1,
    "currentRecordNums": 2
}

response = requests.post(url, json=payload)
result = response.json()

print(result["message"])
```

## 🔌 API Documentation

### Core Classes

#### Launch Task Request
Data model for launching a Privacy Intersection Task (PIT).

```python
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
```

#### Query Status Response
System status information model.

```python
class QueryStatusResponse(BaseModel):
    capacity: int
    availableTaskNum: int
    runningTasks: List[str]
```

#### StopTaskResponse
Response model for stopping a running PIT task.

```python
class StopTaskResponse(BaseModel):
    code: str
    message: str
    data: dict
```
Returned when a task termination request is issued, indicating whether the task
was successfully stopped or not found.

#### PETTaskCallbackRequest
Callback payload model for PET task execution results.

```python
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

```

### REST API Endpoints

Start the API server:
```bash
python -m uvicorn interface:app --reload --host 0.0.0.0 --port 8000 --workers 1
```

Available endpoints:
- POST /SecretFlow/api/v1/pit-tasks - Launch a new PIT computation task.
- GET /SecretFlow/api/v1/status/ - Query current system capacity and running task information.
- DELETE /SecretFlow/api/v1/{task_id} - Stop a running PIT task by task ID.
- POST /SecretFlow/api/v1/callback - Receive PET task execution results and status callbacks.

## 🛡️ Security


## 🧪 Testing

### Running Tests
```bash
# Unit tests
python -m pytest tests/unit -v

# Integration tests  
python -m pytest tests/integration/ --test-data=./test_data/

# Security tests
python -m pytest tests/security/ -v
```

### Test Configuration
Create `test_config.yaml` for testing:

```yaml
test:
  use_mock_data: true
  sample_data_path: "./test_data/samples/"
  validation:
    enabled: true
    strict_mode: false
```

## 🤝 Contributing

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/CharmingCheny/In-House-PET-Enabler.git
```

## 🐛 Troubleshooting

### Common Issues

**Issue: Permission denied errors**


**Issue: Missing dependencies**


**Issue: Configuration errors**


### Getting Help
- **Internal Slack**: `#secretflow-pit-support`
- **Email**: 1155243134@link.cuhk.edu.hk
- **Emergency**: 1155243134@link.cuhk.edu.hk

## 📄 License
This project is licensed under the Apache License, Version 2.0.

You may obtain a copy of the License at:

http://www.apache.org/licenses/LICENSE-2.0


Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
