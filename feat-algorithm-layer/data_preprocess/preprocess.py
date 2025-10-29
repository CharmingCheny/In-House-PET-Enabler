# data_preprocess/preprocess.py
import os
import csv
import psycopg2
import pymysql
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from data_object_utils import get_data_object_metadata

app = FastAPI(title="Data Preprocess Module")

class ExtractRequest(BaseModel):
    dataObjectId: str
    fields: list[str]  
    csvPath: str       

@app.post("/preprocess/extract")
def extract_to_csv(req: ExtractRequest):
    # 1️⃣ Get data source information
    DTM_URL = os.getenv("DTM_URL", "http://127.0.0.1:8001")
    try:
        meta = get_data_object_metadata(DTM_URL, req.dataObjectId)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 2️⃣ Construct a database connection
    ds_type = meta["dataSourceType"].lower()
    address = meta["dataSourceAddress"]
    dbname = meta["dataSourceDbName"]
    user = meta["dataSourceUser"]
    pwd = meta.get("dataSourceCredential")
    table = meta["dataObjectName"]
    fields_str = ",".join(req.fields)

    try:
        if ds_type == "postgresql":
            conn = psycopg2.connect(host=address, database=dbname, user=user, password=pwd)
        elif ds_type == "mysql":
            conn = pymysql.connect(host=address, database=dbname, user=user, password=pwd)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported data source: {ds_type}")

        cursor = conn.cursor()
        sql = f"SELECT {fields_str} FROM {table}"
        cursor.execute(sql)
        rows = cursor.fetchall()

        # 3️⃣ Write to CSV
        with open(req.csvPath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(req.fields)  # Write header
            writer.writerows(rows)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract data: {e}")
    finally:
        cursor.close()
        conn.close()

    return {"code": "00", "message": f"Data extracted to {req.csvPath}", "data": {}}
