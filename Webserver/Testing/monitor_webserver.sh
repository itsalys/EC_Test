#!/bin/bash

# ========== CONFIGURATION ==========
PID=1161                # 🔧 Specify your target PID here
DURATION=120           # Total time to monitor (in seconds)
INTERVAL=1             # Sampling interval for pidstat (seconds)
COUNTDOWN=5            # Delay before starting
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Output files
PERF_FILE="pid_${PID}_perf_stats_${TIMESTAMP}.log"
PIDSTAT_FILE="pid_${PID}_pidstat_log_${TIMESTAMP}.csv"

# ========== VALIDATION ==========

if ! ps -p "$PID" > /dev/null; then
  echo "❌ Error: PID $PID is not running."
  exit 1
fi

# ========== COUNTDOWN ==========
echo "⏳ Starting in $COUNTDOWN seconds..."
for i in $(seq $COUNTDOWN -1 1); do
  echo "$i..."
  sleep 1
done

echo "🟢 Monitoring PID $PID for $DURATION seconds..."

# ========== PIDSTAT ==========
echo "Time,CPU (%),Memory (KB)" > "$PIDSTAT_FILE"
(
  END=$((SECONDS + DURATION))
  while [ $SECONDS -lt $END ]; do
    NOW=$(date +"%Y-%m-%d %H:%M:%S")
    DATA=$(pidstat -p $PID -u -r -h 1 1 | awk 'NR==4 {print $7","$9}')
    echo "$NOW,$DATA" >> "$PIDSTAT_FILE"
  done
) &

# ========== PERF ==========
sudo perf stat \
  -e cycles,instructions,cache-references,cache-misses,branch-misses,context-switches,cpu-migrations,page-faults \
  -p $PID \
  --timeout $((DURATION * 1000)) \
  &> "$PERF_FILE"

echo "✅ Done."
echo "📄 CPU/memory usage logged to: $PIDSTAT_FILE"
echo "📄 Perf stats saved to: $PERF_FILE"
