import paho.mqtt.client as mqtt
import json
import os
from dotenv import load_dotenv

load_dotenv()

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_KEEPALIVE = int(os.getenv("MQTT_KEEPALIVE", 60))

client = mqtt.Client()
callbacks = {}


def on_connect(client, userdata, flags, rc):
    print(f"✅ Connected to MQTT broker with result code {rc}")
    for topic in callbacks:
        client.subscribe(topic)
        print(f"📡 Subscribed to topic: {topic}")


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode("utf-8")
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        print(f"❌ Failed to decode JSON from topic {topic}: {payload}")
        return

    for pattern, callback in callbacks.items():
        if mqtt.topic_matches_sub(pattern, topic):
            callback(topic, data)
            break


def publish_message(topic, payload):
    client.publish(topic, json.dumps(payload))


def register_mqtt_callback(topic, callback):
    callbacks[topic] = callback
    client.subscribe(topic)


def connect_mqtt():
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
    client.loop_start()


# Connect on module import
connect_mqtt()