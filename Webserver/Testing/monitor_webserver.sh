#!/bin/bash

# ===== CONFIGURATION =====
PID=1195                 # 🔧 Set your target PID here
DURATION=60              # Total monitoring time (in seconds)
INTERVAL=1               # Sampling interval for pidstat
COUNTDOWN=5              # Countdown before starting
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# ===== OUTPUT FILES =====
PIDSTAT_FILE="pid_${PID}_cpumem_${TIMESTAMP}.csv"
PERF_FILE="pid_${PID}_perf_${TIMESTAMP}.log"

# ===== VALIDATION =====
if ! ps -p "$PID" > /dev/null; then
  echo "❌ Error: PID $PID is not running."
  exit 1
fi

# ===== COUNTDOWN =====
echo "⏳ Starting in $COUNTDOWN seconds..."
for i in $(seq $COUNTDOWN -1 1); do
  echo "$i..."
  sleep 1
done

echo "🟢 Monitoring PID $PID for $DURATION seconds..."

# ===== START LOGGING =====
# 1. Header for CSV
echo "Time,%CPU,%MEM" > "$PIDSTAT_FILE"

# 2. pidstat logging (CPU and MEM)
pidstat -p $PID -u -r -h $INTERVAL $((DURATION / INTERVAL)) | \
awk -v pid="$PID" '
  $0 ~ /^[0-9]/ && $4 == pid {
    cmd = "date +\"%Y-%m-%d %H:%M:%S\""
    cmd | getline timestamp
    close(cmd)
    print timestamp "," $9 "," $14
  }
' >> "$PIDSTAT_FILE" &

# 3. perf stat run
sudo perf stat \
  -e cycles,instructions,cache-references,cache-misses,branch-misses,context-switches,cpu-migrations,page-faults \
  -p $PID \
  --timeout $((DURATION * 1000)) \
  &> "$PERF_FILE"

# ===== DONE =====
echo "✅ Monitoring complete."
echo "📄 CPU/MEM saved to: $PIDSTAT_FILE"
echo "📄 Perf stats saved to: $PERF_FILE"
