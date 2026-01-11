#!/bin/bash
set -e

# 1. Start Mock DTM (Data Object Manager)
echo "Starting Mock DTM..."
uvicorn data_preprocess.mock_dtm:app --host 127.0.0.1 --port 8001 > logs/mock_dtm.log 2>&1 &
DTM_PID=$!
echo "Mock DTM started with PID $DTM_PID"

# 2. Start Interface API (Alice)
echo "Starting Interface API (Alice)..."
export MOCK_DB_FAILOVER=${MOCK_DB_FAILOVER:-false}
export PARTY=alice

# Try to detect Bob's IP from cluster_alice.yaml if not set
if [ -z "$BOB_HOST" ]; then
    DETECTED_BOB_IP=$(grep -A 2 "bob:" secretflow_core/cluster_alice.yaml | grep "address:" | sed -E 's/.*"([^"]+)".*/\1/' | cut -d':' -f1 | head -n 1)
    if [ ! -z "$DETECTED_BOB_IP" ]; then
        echo "Detected Bob's IP from config: $DETECTED_BOB_IP"
        export BOB_HOST=$DETECTED_BOB_IP
    else
        export BOB_HOST=127.0.0.1
    fi
fi

export BOB_PORT=${BOB_PORT:-8002}
export ALICE_HOST=${ALICE_HOST:-127.0.0.1}

echo "Configuration: ALICE_HOST=$ALICE_HOST, BOB_HOST=$BOB_HOST, BOB_PORT=$BOB_PORT, MOCK_DB_FAILOVER=$MOCK_DB_FAILOVER"

# Note: We no longer automatically update cluster_alice.yaml to avoid overwriting manual changes.
# Please ensure secretflow_core/cluster_alice.yaml is configured correctly.

uvicorn interface.interface:app --host 0.0.0.0 --port 8000 > logs/interface_alice.log 2>&1 &
ALICE_PID=$!
echo "Alice API started with PID $ALICE_PID"

# Wait for services to start
sleep 5

# 3. Run Test Script
echo "Running Test Script..."
python3 interface/test_interface.py

# Cleanup
echo "Stopping services..."
kill $DTM_PID
kill $ALICE_PID
