# /export/coding/mock_dtm.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/framework/data-object/{data_object_id}")
def get_meta(data_object_id: str):
    return {
        "code": "00",
        "message": "ok",
        "data": {
        "dataSourceType": "PostgreSQL",
        "dataSourceAddress": "127.0.0.1",  
        "dataSourceDbName": "testdb",
        "dataSourceUser": "postgres",
        "dataSourceCredential": "passw0rd",
        "dataObjectName": "employee",
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