#!/bin/bash

# ========== CONFIGURATION ==========
PID=1161                 # 🔧 Set your target PID here
DURATION=120             # Total duration to monitor (in seconds)
INTERVAL=1               # Sampling interval in seconds
COUNTDOWN=5              # Optional delay before starting
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Output file
PIDSTAT_FILE="pid_${PID}_accurate_log_${TIMESTAMP}.csv"

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

# ========== PIDSTAT MONITORING ==========
echo "Time,CPU (%),Memory (KB)" > "$PIDSTAT_FILE"

# Start pidstat in continuous mode
pidstat -p $PID -u -r -h $INTERVAL $((DURATION / INTERVAL)) | \
awk 'NR > 3 && $0 !~ /Average/ {
  cmd = "date +\"%Y-%m-%d %H:%M:%S\"";
  cmd | getline timestamp;
  close(cmd);
  print timestamp "," $7 "," $9;
}' >> "$PIDSTAT_FILE"

echo "✅ Done logging."
echo "📄 Saved to: $PIDSTAT_FILE"
