import Inp_Camera.facialRecognition as FR
import Inp_Mic.speechRecognition as SR
import Inp_Ultrasonic.objectDetection as UD
import Out_Speaker.audioFeedback as AF
import time
import socket
import json
import paho.mqtt.client as mqtt

# === Load MQTT Configuration from JSON File ===
with open("config.json") as f:
    config = json.load(f)

BROKER = config["broker"]
PORT = config["port"]
KEEPALIVE = config["keepalive"]

# === MQTT Topics ===
DEVICE_ID = socket.gethostname()
MQTT_TOPIC_REQUEST = f"smartgantry/{DEVICE_ID}/clock_in_request"
MQTT_TOPIC_RESPONSE = f"smartgantry/{DEVICE_ID}/clock_in_response"

# === MQTT Setup ===
response_payload = None  # To store the server's response

def on_message(client, userdata, msg):
    global response_payload
    print(f"MQTT - Received message on {msg.topic}")
    try:
        response_payload = json.loads(msg.payload.decode())
    except json.JSONDecodeError:
        print("[MQTT] Error decoding JSON")

client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, PORT, KEEPALIVE)
client.subscribe(MQTT_TOPIC_RESPONSE)
client.loop_start()

def main():
    global response_payload

    while True:
        distance = UD.measure_distance()
        print(f"Main - Measured Distance: {distance} cm")

        if UD.is_object_in_range(distance, threshold=100):
            print("Main - Object detected within 100 cm. Starting facial recognition...")
            result = FR.facialRecognition()

            if result:
                wake_word = result["name"]
                user_id = result["id"]
                print(f"Main - User recognized: {wake_word} (ID: {user_id}). Initiating speech recognition...")

                speech_detected = SR.speechRecognition(wake_word)

                if speech_detected:
                    print(f"Main - Wake word '{wake_word}' detected. Sending MQTT clock request...")
                    response_payload = None

                    request_payload = {
                        "employee_id": user_id,
                        "action": "clock_in",  # Can be changed dynamically
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                    }

                    client.publish(MQTT_TOPIC_REQUEST, json.dumps(request_payload))

                    timeout = time.time() + 5  # Wait max 5 seconds for reply
                    while time.time() < timeout and response_payload is None:
                        time.sleep(0.1)

                    if response_payload:
                        status = response_payload.get("status")

                        if status == "success":
                            print("[Access Granted] Clock-in confirmed.")
                            AF.play_success_message()

                        elif status == "denied":
                            print(f"[Access Denied] {response_payload.get('message', 'Access denied.')}")
                            AF.play_denied_message()

                        elif status == "error":
                            print(f"[Error] {response_payload.get('message', 'An error occurred during verification.')}")
                            AF.play_error_message()

                        else:
                            print(f"[Error] MQTT - Unexpected status: {status}")
                            AF.play_error_message()
                    else:
                        print("[Error] MQTT - No response received. Access denied.")
                        AF.play_error_message()
                else:
                    print("[Access Denied] Wake word not recognised. Please try again.")
                    AF.play_denied_message()
            else:
                print("[Access Denied] Face not recognized. Please try again.")
                AF.play_denied_message()
        else:
            print("Main - No object detected within 100 cm. Skipping recognition cycle.")

        time.sleep(2)

if __name__ == "__main__":
    main()
