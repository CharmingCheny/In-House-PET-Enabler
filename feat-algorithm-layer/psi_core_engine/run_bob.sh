#!/bin/bash
# run_tasks_alice.sh

echo "=== Task 1 Start ==="
python run_psi.py cluster_bob.yaml ./alice1.csv ./bob1.csv ./alice1_out.csv ./bob1_out.csv id

echo "All tasks completed."