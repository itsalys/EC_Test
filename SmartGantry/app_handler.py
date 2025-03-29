import json
import base64
import os
import socket
import paho.mqtt.client as mqtt
from Inp_Camera.facialRecognition import add_face

import subprocess

def restart_service(service_name):
    try:
        subprocess.run(["sudo", "systemctl", "restart", service_name], check=True)
        print(f"✅ Service '{service_name}' restarted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to restart service '{service_name}':", e)

# === Load config.json ===
CONFIG_FILE = "config.json"

if not os.path.exists(CONFIG_FILE):
    raise FileNotFoundError(f"Missing {CONFIG_FILE}")

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

MQTT_BROKER = config.get("broker", "localhost")
MQTT_PORT = config.get("port", 1883)
MQTT_KEEPALIVE = config.get("keepalive", 60)
MODE = config.get("mode", "unknown")  # 'entry' or 'exit'

# === MQTT Topic → Handler mapping ===
TOPIC_HANDLERS = {
    "app/add_employee/request": "handle_add_employee",
    "app/get_device/request": "handle_device_info_request",
    f"app/update_device/{socket.gethostname()}/request": "handle_mode_update"
}

# === Topic Handlers ===

def handle_add_employee(payload):
    """
    Handles new employee face registration from MQTT message.
    """
    try:
        employee_id = payload.get("employee_id")
        full_name = payload.get("full_name")
        profile_pic_b64 = payload.get("profile_pic")

        if not all([employee_id, full_name, profile_pic_b64]):
            print("Incomplete payload received. Skipping.")
            return

        os.makedirs("temp", exist_ok=True)
        img_path = f"temp/{employee_id}_face.jpg"

        # Save image temporarily
        with open(img_path, "wb") as f:
            f.write(base64.b64decode(profile_pic_b64))

        # Add to FaceDB
        add_face(id=str(employee_id), name=full_name, img_path=img_path)

    finally:
        # Clean up
        if os.path.exists(img_path):
            os.remove(img_path)
            print(f"Deleted temp image: {img_path}")
        
        restart_service("smartgantry.service")

def handle_device_info_request(payload):
    try:
        hostname = socket.gethostname()

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
        except Exception:
            ip_address = "Unable to detect IP"
        finally:
            s.close()

        device_info = {
            "hostname": hostname,
            "ip_address": ip_address,
            "mode": MODE
        }

        response_topic = f"app/get_device/response/{hostname}"
        print(f"Publishing device info to topic: {response_topic}")
        client.publish(response_topic, json.dumps(device_info))

    except Exception as e:
        print(f"Failed to generate or send device info: {e}")

def handle_mode_update(payload):
    global MODE
    mode = payload.get("mode")
    hostname = socket.gethostname()

    response_topic = f"app/update_device/{hostname}/response"
    
    if mode not in ["entry", "exit"]:
        print(f"Invalid mode: {mode}")
        client.publish(response_topic, json.dumps({"status": "error", "message": "Invalid mode"}))
        return

    config_path = "config.json"
    try:
        with open(config_path, "r") as f:
            config = json.load(f)

        config["mode"] = mode
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)

        restart_service("smartgantry.service")
        
        MODE = mode
        print(f"Device mode updated to: {MODE}")

        client.publish(response_topic, json.dumps({"status": "success", "message": f"Mode changed to {mode}"}))
    except Exception as e:
        print(f"Failed to update mode: {e}")
        client.publish(response_topic, json.dumps({"status": "error", "message": str(e)}))


# === Dispatcher ===

def dispatch(topic, payload):
    handler_name = TOPIC_HANDLERS.get(topic)
    if not handler_name:
        print(f"No handler registered for topic: {topic}")
        return

    handler_func = globals().get(handler_name)
    if callable(handler_func):
        handler_func(payload)
    else:
        print(f"Handler function '{handler_name}' not found.")

# === MQTT Callbacks ===

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker")
        for topic in TOPIC_HANDLERS:
            client.subscribe(topic)
            print(f"Subscribed to topic: {topic}")
    else:
        print(f"Connection failed with return code: {rc}")

def on_message(client, userdata, msg):
    print(f"Message received on topic: {msg.topic}")
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        dispatch(msg.topic, payload)
    except Exception as e:
        print(f"Error processing message: {e}")

# === MQTT Client Setup ===

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print(f"Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}...")
client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
client.loop_forever()
