import json
import os
import base64
import socket
import paho.mqtt.client as mqtt
from Inp_Camera.facialRecognition import add_face

CONFIG_FILE = "config.json"

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

MQTT_BROKER = config["broker"]
MQTT_PORT = config["port"]
MQTT_KEEPALIVE = config["keepalive"]
MODE = config.get("mode", "unknown")

TOPIC_HANDLERS = {
    "app/add_employee/request": "handle_add_employee",
    "app/device_management/request": "handle_device_info_request",
    f"app/update_device/{socket.gethostname()}": "handle_mode_update"
}

def handle_add_employee(payload):
    employee_id = payload.get("employee_id")
    full_name = payload.get("full_name")
    profile_pic_b64 = payload.get("profile_pic")

    if not all([employee_id, full_name, profile_pic_b64]):
        return

    os.makedirs("temp", exist_ok=True)
    img_path = f"temp/{employee_id}_face.jpg"

    with open(img_path, "wb") as f:
        f.write(base64.b64decode(profile_pic_b64))

    add_face(id=str(employee_id), name=full_name, img_path=img_path)

    os.remove(img_path)

def handle_device_info_request(_):
    hostname = socket.gethostname()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
    except:
        ip_address = "Unknown"
    finally:
        s.close()

    device_info = {
        "hostname": hostname,
        "ip_address": ip_address,
        "mode": MODE
    }

    response_topic = f"app/device_management/response/{hostname}"
    client.publish(response_topic, json.dumps(device_info))

def handle_mode_update(payload):
    new_mode = payload.get("mode")
    if new_mode not in ["entry", "exit"]:
        return

    with open(CONFIG_FILE, "r+") as f:
        config = json.load(f)
        config["mode"] = new_mode
        f.seek(0)
        json.dump(config, f, indent=4)
        f.truncate()

    hostname = socket.gethostname()
    confirm_topic = f"app/update_device/confirm/{hostname}"
    client.publish(confirm_topic, json.dumps({"status": "updated"}))

def dispatch(topic, payload):
    for pattern in TOPIC_HANDLERS:
        if mqtt.topic_matches_sub(pattern, topic):
            handler = globals().get(TOPIC_HANDLERS[pattern])
            if callable(handler):
                handler(payload)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        for topic in TOPIC_HANDLERS:
            client.subscribe(topic)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        dispatch(msg.topic, payload)
    except:
        pass

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
client.loop_forever()
