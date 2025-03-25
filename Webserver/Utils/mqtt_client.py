# Utils/mqtt_client.py

import os
import json
import threading
import paho.mqtt.client as mqtt

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_KEEPALIVE = int(os.getenv("MQTT_KEEPALIVE", 60))

# Callback registry
_topic_callbacks = {}
_subscriber_client = mqtt.Client()

def publish_message(topic, payload):
    """Publish a JSON message to a given MQTT topic."""
    try:
        pub_client = mqtt.Client()
        pub_client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
        pub_client.publish(topic, json.dumps(payload))
        pub_client.disconnect()
    except Exception as e:
        print(f"MQTT Publish Error: {e}")

def register_mqtt_callback(topic_pattern, callback):
    """Register a callback to be invoked when a message is received on a specific topic."""
    _topic_callbacks[topic_pattern] = callback
    _subscriber_client.subscribe(topic_pattern)

def _on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT client connected")
        for topic in _topic_callbacks.keys():
            client.subscribe(topic)
            print(f"Subscribed to {topic}")
    else:
        print(f"MQTT connection failed with code {rc}")

def _on_message(client, userdata, msg):
    for pattern, callback in _topic_callbacks.items():
        if mqtt.topic_matches_sub(pattern, msg.topic):
            try:
                payload = json.loads(msg.payload.decode("utf-8"))
                callback(msg.topic, payload)
            except Exception as e:
                print(f"Error handling MQTT message on {msg.topic}: {e}")
            break

def start_mqtt_subscriber():
    """Start background MQTT subscriber loop."""
    _subscriber_client.on_connect = _on_connect
    _subscriber_client.on_message = _on_message

    def loop():
        try:
            _subscriber_client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
            _subscriber_client.loop_forever()
        except Exception as e:
            print(f"MQTT subscriber failed to start: {e}")

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()

def reconnect_subscriber():
    """Forcefully disconnect and reconnect the subscriber to ignore old messages."""
    try:
        _subscriber_client.disconnect()
        print("MQTT subscriber manually disconnected for fresh scan.")
    except Exception as e:
        print(f"Error during MQTT subscriber disconnect: {e}")

    # Reconnect in a short thread
    def reconnect():
        try:
            _subscriber_client.reconnect()
            print("MQTT subscriber reconnected.")
        except Exception as e:
            print(f"MQTT subscriber reconnect failed: {e}")

    threading.Thread(target=reconnect, daemon=True).start()


# Initialise on import
start_mqtt_subscriber()
