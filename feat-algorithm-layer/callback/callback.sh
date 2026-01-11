#!/bin/bash

# 1. Define variables
TASK_ID="task-20251203"
CALLBACK_URL="http://localhost:8000/SecretFlow/api/v1/callback"
# Note: Ensure this path is correct relative to where the PSI script is run
PSI_OUTPUT="./output/alice_psi_10:10_out.csv" 
JOIN_KEY="id"

echo ">>> Step 1: Running PSI Algorithm..."
# Execute the previous run_psi.py (no changes needed to the original code)
# Note: This script is only responsible for generating the CSV, not the callback
python run_psi.py cluster_alice.yaml ./alice_psi_N10.csv ./bob_psi_N10.csv ./output/alice_psi_10:10_out.csv ./output/bob_psi_10:10_out.csv id

# Check the exit status of the previous command
if [ $? -eq 0 ]; then
    echo ">>> PSI Algorithm Success. Starting Result Process..."
    
    # 2. Execute the Result Process script
    # Parameters here are filled according to your API documentation requirements
    python post_result.py \
        --result_file $PSI_OUTPUT \
        --task_id $TASK_ID \
        --callback_url $CALLBACK_URL \
        --join_key $JOIN_KEY \
        --req_data_id "data-obj-alice-001" \
        --col_data_id "data-obj-bob-002" \
        --block_size 500  # Set block size to 500 records per batch
        
    # Optional: Check the exit status of post_result.py as well
    if [ $? -ne 0 ]; then
        echo ">>> Result Process (Callback) Failed. Exiting."
        exit 1
    fi
else
    echo ">>> PSI Algorithm Failed. Skipping Result Process."
    # Optional: You could write a separate call here to send taskResultStatusCode="01" (FAILURE) to the API
    exit 1
fi