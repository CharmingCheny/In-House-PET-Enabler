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

**PrivacyGuard** is an enterprise-grade tool designed to protect sensitive information during internal data processing and sharing. It combines multiple redaction strategies with strong encryption to ensure privacy compliance while maintaining data utility for authorized purposes.

**Key Capabilities:**
- Automated PII (Personally Identifiable Information) detection and classification
- Multiple redaction techniques: masking, encryption, tokenization
- Support for various data formats:
- Comprehensive audit logging for compliance tracking


## ✨ Features

### 🔍 Smart Detection
- **Pattern-based Detection**: Regex patterns for emails, phones, IDs, and custom formats
- **Contextual Analysis**: NLP-based identification of sensitive information in context
- **Custom Rules**: Organization-specific detection patterns and policies

### 🛡️ Multiple Protection Methods
- **Data Masking**: Partial or full redaction of sensitive fields
- **Encryption**: AES-256 encryption for reversible protection
- **Tokenization**: Replace sensitive data with non-sensitive tokens
- **Format-Preserving**: Maintain data format while protecting content

### 📊 Data Format Support
- **Text Documents**: TXT, PDF, DOCX
- **Structured Data**: CSV, JSON, XML
- **Batch Processing**: Directory-level processing for large datasets
- **Stream Processing**: Real-time data protection for APIs

## 🏗️ Architecture Overview

```mermaid
graph TD
    A[Input Data] --> B(PII Detection Engine)
    B --> C{Redaction Policy}
    C --> D[Data Masking]
    C --> E[Encryption]
    C --> F[Tokenization]
    D --> G[Redacted Output]
    E --> G
    F --> G
```

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- 4GB RAM minimum, 8GB recommended
- 500MB free disk space

### Quick Installation
```bash
# Clone the repository (internal network only)
git clone https://github.internal.com/security/privacy-guard.git
cd privacy-guard

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import privacy_guard; print('Installation successful!')"
```

### Docker Installation
```bash
# Pull from internal registry
docker pull internal.registry.com/security/privacy-guard:latest

# Run container
docker run -p 8000:8000 -v $(pwd)/data:/app/data privacy-guard
```

## ⚡ Quick Start

### Command Line Interface
```bash
# Basic file redaction
python privacy_guard.py redact --input sensitive_data.csv --output redacted_data.csv

# Specific field redaction
python privacy_guard.py process \
    --input-dir ./sensitive_docs/ \
    --output-dir ./protected_docs/ \
    --fields email,phone,ssn \
    --method encrypt

# Batch processing with statistics
python privacy_guard.py batch \
    --config config.yaml \
    --stats-dir ./reports/
```

### Python API
```python
from privacy_guard import PrivacyEngine, ProtectionConfig

# Initialize with default configuration
guard = PrivacyEngine()

# Basic text redaction
sensitive_text = "Contact John Doe at john.doe@company.com or (555) 123-4567"
redacted_text = guard.redact_text(sensitive_text)
print(redacted_text)  # "Contact [REDACTED] at [REDACTED] or [REDACTED]"

# Process DataFrame with specific rules
import pandas as pd
df = pd.read_csv('sensitive_data.csv')
protected_df = guard.protect_dataframe(df, fields=['email', 'phone'])
```

## ⚙️ Configuration

### Basic Configuration File


### Environment Variables
```bash
# Required environment variables
export PG_ENCRYPTION_KEY="your-encryption-key-here"
export PG_DB_URL="postgresql://user:pass@localhost/privacy_guard"
export PG_LOG_LEVEL="INFO"

# Optional variables
export PG_MAX_FILE_SIZE="100MB"
```

## 💻 Usage Examples

### Example 1: Document Redaction
```python
from privacy_guard import DocumentProcessor

processor = DocumentProcessor("config.yaml")

# Process a single document
result = processor.process_document(
    input_path="sensitive_report.pdf",
    output_path="redacted_report.pdf",
    methods={"names": "mask", "emails": "encrypt"}
)

print(f"Redacted {result.fields_redacted} fields")
```

### Example 2: Database Protection
```python
from privacy_guard import DatabaseGuard

# Protect database columns
db_guard = DatabaseGuard("postgresql://localhost/mydb")

protected_data = db_guard.protect_table(
    table_name="users",
    columns=["email", "phone_number", "social_security"],
    method="tokenize"
)
```

### Example 3: API Integration
```python
from flask import Flask, request, jsonify
from privacy_guard import PrivacyEngine

app = Flask(__name__)
guard = PrivacyEngine()

@app.route('/api/protect', methods=['POST'])
def protect_data():
    data = request.json
    protected_data = guard.redact_text(data['text'])
    return jsonify({"protected_text": protected_data})

if __name__ == '__main__':
    app.run(port=8000)
```

## 🔌 API Documentation

### Core Classes

#### PrivacyEngine
Main class for privacy protection operations.

```python
class PrivacyEngine:
    def __init__(self, config_path: str = None):
        """
        Initialize PrivacyEngine with optional configuration.
        
        Args:
            config_path: Path to configuration file
        """
    
    def redact_text(self, text: str, methods: dict = None) -> str:
        """Redact sensitive information from text"""
        
    def protect_dataframe(self, df, fields: list, method: str = "mask") -> pd.DataFrame:
        """Protect sensitive columns in a DataFrame"""
```

#### ProtectionConfig
Configuration management class.

```python
class ProtectionConfig:
    def __init__(self, config_dict: dict = None):
        """Initialize with configuration dictionary"""
    
    def validate(self) -> bool:
        """Validate configuration settings"""
    
    def update_pattern(self, pattern_name: str, pattern_config: dict):
        """Update detection patterns"""
```

### REST API Endpoints

Start the API server:
```bash
python -m privacy_guard.api --port 8000 --host 0.0.0.0
```

Available endpoints:
- `POST /api/v1/redact` - Redact text content
- `POST /api/v1/batch` - Batch process multiple files
- `GET /api/v1/health` - Health check
- `GET /api/v1/stats` - Processing statistics

## 🛡️ Security

### Encryption Standards
- **AES-256-GCM** for strong encryption
- **Secure Key Management** with regular rotation
- **TLS 1.3** for all network communications
- **Secure Defaults** following industry best practices

### Access Control
- Role-based access control (RBAC) for internal teams
- Multi-factor authentication support
- API key management with expiration
- Audit trails for all operations

### Compliance Features
- **GDPR Compliance**: Right to be forgotten implementation
- **HIPAA Support**: Healthcare data protection
- **Audit Logging**: Comprehensive activity tracking
- **Data Retention**: Configurable retention policies

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
git clone https://github.internal.com/your-username/privacy-guard.git
```

## 🐛 Troubleshooting

### Common Issues

**Issue: Permission denied errors**
```bash
# Solution: Run with appropriate permissions
sudo python privacy_guard.py [options]
# Or add your user to the required groups
```

**Issue: Missing dependencies**
```bash
# Solution: Reinstall requirements
pip install -r requirements.txt
```

**Issue: Configuration errors**
```bash
# Solution: Validate config file
python -m privacy_guard.validate_config config.yaml
```

### Getting Help
- **Internal Slack**: `#privacy-tool-support`
- **Email**: privacy-tool-team@company.com
- **Emergency**: security-incident@company.com

## 📄 License

This tool is proprietary software owned by your organization. Internal use only under the terms of the Internal Software License Agreement.