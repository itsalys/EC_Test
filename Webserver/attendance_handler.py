import os
import json
import pymysql
import paho.mqtt.client as mqtt
from datetime import datetime
from datetime import timezone
from datetime import timedelta
import pytz  # ? Add this

from dotenv import load_dotenv

# === Load Environment Variables ===
load_dotenv()

BROKER = os.getenv("BROKER")
PORT = int(os.getenv("PORT"))
KEEPALIVE = int(os.getenv("KEEPALIVE"))
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# === Database Connection ===
def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

# === MQTT Callback ===
def on_message(client, userdata, msg):
    print(f"[MQTT] Received message on topic: {msg.topic}")
    try:
        parts = msg.topic.split('/')
        if len(parts) != 3 or not parts[2].endswith("_request"):
            print("[ERROR] Invalid topic format.")
            return
        device_id = parts[1]
        action = parts[2].replace("_request", "")
        payload = json.loads(msg.payload.decode())
        handle_attendance(device_id, action, payload)
    except Exception as e:
        print(f"[ERROR] Failed to process message: {e}")

def handle_attendance(device_id, action, payload):
    employee_id = payload.get("employee_id")
    timestamp = payload.get("timestamp")

    if not all([employee_id, action, timestamp]):
        send_response(device_id, action, "error", "Incomplete request payload.")
        return

    try:
        utc_dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        sg_time = utc_dt.astimezone(pytz.timezone("Asia/Singapore"))
        parsed_timestamp = sg_time

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM attendance
                WHERE employee_id = %s
                ORDER BY timestamp DESC
                LIMIT 1;
            """, (employee_id,))
            latest = cursor.fetchone()

        if action == "clock_in":
            if latest and latest["clocked_in"] == 1:
                send_response(device_id, action, "error", "Employee is already clocked in.")
            else:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO attendance (employee_id, timestamp, clocked_in)
                        VALUES (%s, %s, 1);
                    """, (employee_id, parsed_timestamp))  # ✅ use adjusted timestamp
                    conn.commit()
                send_response(device_id, action, "success", "Clock-in confirmed.")

        elif action == "clock_out":
            if latest is None:
                send_response(device_id, action, "error", "No prior record found. Clock-out denied.")
            elif latest["clocked_in"] == 0:
                send_response(device_id, action, "error", "Employee is already clocked out.")
            else:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO attendance (employee_id, timestamp, clocked_in)
                        VALUES (%s, %s, 0);
                    """, (employee_id, parsed_timestamp))  # ✅ use adjusted timestamp
                    conn.commit()
                send_response(device_id, action, "success", "Clock-out confirmed.")

        else:
            send_response(device_id, action, "error", f"Unsupported action: {action}")
    except Exception as e:
        print(f"[ERROR] {e}")
        send_response(device_id, action, "error", "Internal server error.")

def send_response(device_id, action, status, message):
    topic = f"smartgantry/{device_id}/{action}_response"
    payload = {
        "status": status,
        "message": message
    }
    client.publish(topic, json.dumps(payload))
    print(f"[MQTT] Sent response to {topic}: {payload}")

# === MQTT Init ===
client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, PORT, KEEPALIVE)
client.subscribe("smartgantry/+/clock_in_request")
client.subscribe("smartgantry/+/clock_out_request")
client.loop_forever()
