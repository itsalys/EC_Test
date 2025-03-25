import os
import base64
import json
import paho.mqtt.client as mqtt

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))

mqtt_client = mqtt.Client()

def publish_message(topic, payload):
    """Publish a JSON message to a given MQTT topic."""
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.publish(topic, json.dumps(payload))
        mqtt_client.disconnect()
    except Exception as e:
        print(f"❌ MQTT Publish Error: {e}")
