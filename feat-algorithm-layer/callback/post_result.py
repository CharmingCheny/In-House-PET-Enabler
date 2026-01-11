import pandas as pd
import requests
import argparse
import sys
import json
import math

def send_callback(url, payload):
    """Sends HTTP POST request to the callback interface."""
    headers = {'Content-Type': 'application/json'}
    response = None # Initialize response outside try block for access in except
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status() # Raises an exception for HTTP error codes (4xx or 5xx)
        print(f"✅ [Block {payload['currentBlockNum']}/{payload['totalBlockNums']}] Upload success. API Code: {response.json().get('code')}")
        return True
    except Exception as e:
        print(f"❌ [Block {payload['currentBlockNum']}] Upload failed: {e}")
        if response is not None:
             print(f"Server Response: {response.text}")
        return False

def process_and_send(args):
    """Reads the CSV and sends data in chunks (blocks)."""
    
    # 1. Read the PSI result file
    try:
        # Assuming the PSI result is a CSV and contains the join_key column
        df = pd.read_csv(args.result_file)
        total_records = len(df)
        print(f"📊 Loaded result file: {args.result_file}, Total records: {total_records}")
    except Exception as e:
        print(f"❌ Failed to read result file: {e}")
        sys.exit(1)

    # 2. Calculate the number of blocks
    block_size = args.block_size
    total_blocks = math.ceil(total_records / block_size)
    
    if total_blocks == 0:
        total_blocks = 1 # Send notification once even if empty

    # 3. Iterate through each block and send
    for block_idx in range(total_blocks):
        start_idx = block_idx * block_size
        end_idx = min((block_idx + 1) * block_size, total_records)
        
        # Get data for the current block
        chunk_df = df.iloc[start_idx:end_idx]
        current_record_nums = len(chunk_df)

        # 4. Construct resultValueList
        # Format example: [{"field1": "value1", "resultFlag": true}, ...]
        result_value_list = []
        for _, row in chunk_df.iterrows():
            item = {}
            # Dynamically retrieve the value of the join_key
            key_value = str(row[args.join_key])
            
            # Construct the dictionary, assuming the field name is the join_key
            item[args.join_key] = key_value 
            item["resultFlag"] = True # PSI intersection result typically implies True
            
            result_value_list.append(item)

        # 5. Construct the complete Request Body
        payload = {
            "taskId": args.task_id,
            "taskResultStatusCode": "00", # 00 means success
            "message": "PSI Task execution successful",
            
            # The following IDs should be passed from upstream in production, here they are arguments or default values
            "requesterDataObjectId": args.req_data_id,
            "collaboratorDataObjectId": args.col_data_id,
            
            "collaboratorFields": [args.join_key],
            "algorithmSource": "SecretFlow",
            "algorithmProtocol": "PROTOCOL_RR22", # Or ECDN-PSI depending on the actual situation
            "algorithmVersion": "V1.0",
            "logicFormula": args.join_key, # Simple intersection logic
            "valueFields": [args.join_key],
            
            # Core Data
            "resultValueList": result_value_list,
            
            # Pagination Information
            "totalBlockNums": total_blocks,
            "currentBlockNum": block_idx + 1, # block count starts from 1
            "currentRecordNums": current_record_nums
        }

        # 6. Send Callback
        success = send_callback(args.callback_url, payload)
        if not success:
            print("⚠️ Stopping process due to callback failure.")
            sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Result Process: Send PSI results to Callback API")
    
    # Required arguments
    parser.add_argument("--result_file", required=True, help="Path to the PSI result CSV file")
    parser.add_argument("--task_id", required=True, help="Unique Task ID")
    parser.add_argument("--callback_url", required=True, help="Target API URL")
    parser.add_argument("--join_key", required=True, help="The column name used for PSI")
    
    # Optional arguments (based on metadata in the documentation)
    parser.add_argument("--req_data_id", default="unknown-req-id", help="Requester Data Object ID")
    parser.add_argument("--col_data_id", default="unknown-col-id", help="Collaborator Data Object ID")
    parser.add_argument("--block_size", type=int, default=1000, help="Number of records per callback request")

    args = parser.parse_args()
    
    process_and_send(args)