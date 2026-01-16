from fastapi import FastAPI

app = FastAPI()

@app.get("/framework/data-object/{data_object_id}")
def get_meta(data_object_id: str):
    # 这里可以根据 data_object_id 返回不同的配置
    # 但为了演示简单，我们统一返回您提供的 MySQL 配置
    
    # 确保两台机器上的 MySQL 都有这个库和表
    return {
        "code": "00",
        "message": "ok",
        "data": {
            "dataSourceType": "MySQL",           # 修改为 MySQL
            "dataSourceAddress": "127.0.0.1",    # 这里的 127.0.0.1 指的是运行该 Python 脚本的机器本地
            "dataSourceDbName": "testdb",
            "dataSourceUser": "appuser",
            "dataSourceCredential": "app_pass",
            "dataObjectName": "employee",        # 确保 MySQL 中表名一致
            "dataElementList": [
                {"data_elem_fid_name": "emp_no", "data_elem_fid_type": "String", "data_elem_fid_len": "20", "data_elem_fid_scale": ""},
                {"data_elem_fid_name": "name", "data_elem_fid_type": "String", "data_elem_fid_len": "100", "data_elem_fid_scale": ""},
                {"data_elem_fid_name": "department", "data_elem_fid_type": "String", "data_elem_fid_len": "100", "data_elem_fid_scale": ""},
                {"data_elem_fid_name": "email", "data_elem_fid_type": "String", "data_elem_fid_len": "200", "data_elem_fid_scale": ""},
                {"data_elem_fid_name": "salary", "data_elem_fid_type": "Numeric", "data_elem_fid_len": "12", "data_elem_fid_scale": "2"},
                {"data_elem_fid_name": "hire_date", "data_elem_fid_type": "Date", "data_elem_fid_len": "", "data_elem_fid_scale": ""}
            ]
        }
    }
