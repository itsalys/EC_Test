#!/bin/bash

SERVICE_NAME="attendance-handler.service"
DURATION=120           # Total time to monitor (in seconds)
INTERVAL=1             # Sampling interval for pidstat (seconds)
COUNTDOWN=5            # Countdown before start
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Output files
PERF_FILE="attendance-handler_perf_stats_${TIMESTAMP}.log"
PIDSTAT_FILE="attendance-handler_pidstat_log_${TIMESTAMP}.csv"

# Get PID
PID=$(systemctl show -p MainPID "$SERVICE_NAME" | cut -d= -f2)

if [ "$PID" -eq "0" ]; then
  echo "❌ Error: Service '$SERVICE_NAME' is not running."
  exit 1
fi

# Countdown before monitoring
echo "⏳ Starting in $COUNTDOWN seconds..."
for i in $(seq $COUNTDOWN -1 1); do
  echo "$i..."
  sleep 1
done

echo "🟢 Monitoring PID $PID of $SERVICE_NAME for $DURATION seconds..."

# Start pidstat (records every INTERVAL seconds)
echo "Time,CPU (%),Memory (KB)" > "$PIDSTAT_FILE"
(
  END=$((SECONDS + DURATION))
  while [ $SECONDS -lt $END ]; do
    NOW=$(date +"%Y-%m-%d %H:%M:%S")
    DATA=$(pidstat -p $PID -u -r -h 1 1 | awk 'NR==4 {print $7","$9}')
    echo "$NOW,$DATA" >> "$PIDSTAT_FILE"
  done
) &

# Start perf stat (runs for full duration)
sudo perf stat \
  -e cycles,instructions,cache-references,cache-misses,branch-misses,context-switches,cpu-migrations,page-faults \
  -p $PID \
  --timeout $((DURATION * 1000)) \
  &> "$PERF_FILE"

echo "✅ Done."
echo "📄 CPU/memory usage logged to: $PIDSTAT_FILE"
echo "📄 Perf stats saved to: $PERF_FILE"
