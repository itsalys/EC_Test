#!/bin/bash

# ====== CONFIG ======
PID=1161                    # Set your PID here
DURATION=120                # Max monitoring time in seconds
INTERVAL=1                  # Sampling interval
COUNTDOWN=5                 # Optional delay
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
PIDSTAT_FILE="pid_${PID}_livequit_log_${TIMESTAMP}.csv"

# ====== CHECK ======
if ! ps -p "$PID" > /dev/null; then
  echo "❌ PID $PID not found or not running."
  exit 1
fi

# ====== COUNTDOWN ======
echo "⏳ Starting in $COUNTDOWN seconds..."
for i in $(seq $COUNTDOWN -1 1); do
  echo "$i..."
  sleep 1
done

# ====== HEADER ======
echo "Time,CPU (%),Memory (KB)" > "$PIDSTAT_FILE"

# ====== KEYPRESS MONITOR ======
stop_flag=false
(
  while true; do
    read -r -n1 -s key
    if [[ "$key" == "q" ]]; then
      echo -e "\n🛑 'q' pressed. Stopping..."
      stop_flag=true
      break
    fi
  done
) &

KEY_PID=$!

# ====== START pidstat ======
{
  pidstat -p $PID -u -r -h $INTERVAL | \
  awk '
    NR > 3 && $0 !~ /Average/ {
      cmd = "date +\"%Y-%m-%d %H:%M:%S\"";
      cmd | getline timestamp;
      close(cmd);
      print timestamp "," $7 "," $9;
      fflush();
    }
  '
} >> "$PIDSTAT_FILE" &

PIDSTAT_PID=$!

# ====== WATCH & KILL IF NEEDED ======
START_TIME=$(date +%s)
while true; do
  sleep 1

  # Stop if process no longer exists
  if ! ps -p "$PID" > /dev/null; then
    echo "⚠️ Process $PID has exited."
    break
  fi

  # Stop if time exceeded
  NOW=$(date +%s)
  if (( NOW - START_TIME >= DURATION )); then
    echo "⏱️ Max duration reached."
    break
  fi

  # Stop if 'q' pressed
  if $stop_flag; then
    break
  fi
done

# Cleanup
kill "$PIDSTAT_PID" 2>/dev/null
kill "$KEY_PID" 2>/dev/null

echo "✅ Monitoring stopped."
echo "📄 Output saved to: $PIDSTAT_FILE"
