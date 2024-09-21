#!/bin/bash

execution_number=0
  # Wait time between checks in seconds.

while true; do
  wait_time=3600
  # Get the current hour
  current_hour=$(date +%H)

  # Check if the current hour is between 6 AM and 12 AM
  if [ "$current_hour" -ge 6 ] && [ "$current_hour" -lt 24 ]; then
  execution_number=$((execution_number + 1))
  echo "------------------------ Execution: $execution_number. Wait time $wait_time. --------------------------"
  python3 main.py
  python3 db_process.py
  fi
  sleep $wait_time
done
