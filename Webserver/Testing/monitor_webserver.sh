#!/bin/bash

# ========== CONFIGURATION ==========
PID=1161                 # 🔧 Set your target PID here
DURATION=120             # Total time to monitor (in seconds)
INTERVAL=1               # Sampling interval for pidstat
COUNTDOWN=5              # Delay before starting
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Output files
PIDSTAT_FILE="pid_${PID}_accurate_log_${TIMESTAMP}.csv"
PERF_FILE="pid_${PID}_perf_stats_${TIMESTAMP}.log"

# ========== VALIDATION ==========
if ! ps -p "$PID" > /dev/null; then
  echo "❌ Error: PID $PID is not running."
  exit 1
fi

# ========== COUNTDOWN ==========
echo "⏳ Monitoring will start in $COUNTDOWN seconds..."
for i in $(seq $COUNTDOWN -1 1); do
  echo "$i..."
  sleep 1
done

# ========== PIDSTAT ==========
echo "🟢 Starting pidstat monitoring for PID $PID..."
echo "Time,CPU (%),Memory (KB)" > "$PIDSTAT_FILE"

pidstat -p $PID -u -r -h $INTERVAL $((DURATION / INTERVAL)) | \
awk 'NR > 3 && $0 !~ /Average/ {
  cmd = "date +\"%Y-%m-%d %H:%M:%S\"";
  cmd | getline timestamp;
  close(cmd);
  print timestamp "," $7 "," $9;
}' >> "$PIDSTAT_FILE" &

# ========== PERF ==========
echo "🟢 Starting perf stat for PID $PID..."
sudo perf stat \
  -e cycles,instructions,cache-references,cache-misses,branch-misses,context-switches,cpu-migrations,page-faults \
  -p $PID \
  --timeout $((DURATION * 1000)) \
  &> "$PERF_FILE"

# ========== DONE ==========
echo "✅ Monitoring complete."
echo "📄 CPU/memory usage saved to: $PIDSTAT_FILE"
echo "📄 Performance counters saved to: $PERF_FILE"
