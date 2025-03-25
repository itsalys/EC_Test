import json
import base64
import os
import paho.mqtt.client as mqtt
from Inp_Camera.facialRecognition import add_face

# === Load config.json ===
CONFIG_FILE = "config.json"

if not os.path.exists(CONFIG_FILE):
    raise FileNotFoundError(f"Missing {CONFIG_FILE}")

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

MQTT_BROKER = config.get("broker", "localhost")
MQTT_PORT = config.get("port", 1883)
MQTT_KEEPALIVE = config.get("keepalive", 60)

# === MQTT Topic → Handler mapping ===
TOPIC_HANDLERS = {
    "app/add_employee/request": "handle_add_employee"
    # Add more mappings here
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
            print("⚠️ Incomplete payload received. Skipping.")
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
            print(f"🧹 Deleted temp image: {img_path}")

# === Dispatching by topic ===
def dispatch(topic, payload):
    handler_name = TOPIC_HANDLERS.get(topic)
    if not handler_name:
        print(f"⚠️ No handler registered for topic: {topic}")
        return

    handler_func = globals().get(handler_name)
    if callable(handler_func):
        handler_func(payload)
    else:
        print(f"❌ Handler function '{handler_name}' not found.")

# === MQTT Callbacks ===
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT Broker")
        for topic in TOPIC_HANDLERS:
            client.subscribe(topic)
            print(f"📡 Subscribed to topic: {topic}")
    else:
        print(f"❌ Connection failed with return code: {rc}")

def on_message(client, userdata, msg):
    print(f"\n📩 Message received on {msg.topic}")
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        dispatch(msg.topic, payload)
    except Exception as e:
        print(f"❌ Failed to handle message: {e}")

# === MQTT Client Setup ===
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print(f"🔌 Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}...")
client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
client.loop_forever()
