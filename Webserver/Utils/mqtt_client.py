import os
import base64
import paho.mqtt.client as mqtt

# Configure MQTT Broker details from env or hardcode for testing
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "employee/new")

# Initialise MQTT client
mqtt_client = mqtt.Client()

def publish_new_employee(employee_id, full_name, profile_pic_binary):
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        profile_pic_b64 = base64.b64encode(profile_pic_binary).decode("utf-8")

        payload = {
            "employee_id": employee_id,
            "full_name": full_name,
            "profile_pic": profile_pic_b64
        }

        import json
        mqtt_client.publish(MQTT_TOPIC, json.dumps(payload))
        mqtt_client.disconnect()
    except Exception as e:
        print(f"❌ MQTT Publish Error: {e}")
