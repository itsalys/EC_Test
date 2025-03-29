#!/bin/bash

SERVICE_NAME="webserver.service"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="perf_webserver_${TIMESTAMP}.log"
DURATION=120  # Duration in seconds (change as needed)

# Get the MainPID of the service
PID=$(systemctl show -p MainPID "$SERVICE_NAME" | cut -d= -f2)

if [ "$PID" -eq "0" ]; then
  echo "❌ Error: Service '$SERVICE_NAME' is not running."
  exit 1
fi

echo "🟢 Monitoring service '$SERVICE_NAME' (PID $PID) with perf for $DURATION seconds..."
sudo perf stat \
  -e cycles,instructions,cache-references,cache-misses,branch-misses,context-switches,cpu-migrations,page-faults \
  -p $PID \
  --timeout ${DURATION}000 \
  &> "$OUTPUT_FILE"

echo "✅ perf stats saved to $OUTPUT_FILE"
