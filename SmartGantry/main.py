import Inp_Camera.facialRecognition as FR
import Inp_Mic.speechRecognition as SR
import Inp_Ultrasonic.objectDetection as UD
import Out_Speaker.audioFeedback as AF
from ui_manager import UIManager
import time
import socket
import json
import paho.mqtt.client as mqtt

ui = UIManager()

# === Load MQTT Configuration from JSON File ===
with open("config.json") as f:
    config = json.load(f)

BROKER = config["broker"]
PORT = config["port"]
KEEPALIVE = config["keepalive"]
MODE = config["mode"].lower()  # either "entry" or "exit"

# === MQTT Topics Based on Mode ===
DEVICE_ID = socket.gethostname()
if MODE == "entry":
    ACTION = "clock_in"
elif MODE == "exit":
    ACTION = "clock_out"
else:
    raise ValueError("Invalid mode in config.json. Use 'entry' or 'exit'.")

MQTT_TOPIC_REQUEST = f"smartgantry/{DEVICE_ID}/{ACTION}_request"
MQTT_TOPIC_RESPONSE = f"smartgantry/{DEVICE_ID}/{ACTION}_response"

# === MQTT Setup ===
response_payload = None

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
    screen_on = False  # Track screen state

    while True:
        distance = UD.measure_distance()
        print(f"Main - Measured Distance: {distance} cm")

        if UD.is_object_in_range(distance, threshold=100):
            if not screen_on:
                ui.show_ui()
                screen_on = True

            print("Main - Object detected within 100 cm. Starting facial recognition...")
            ui.show_message("Please look at the camera for verification...", "white")
            time.sleep(2)

            result = FR.facialRecognition()

            if result:
                wake_word = result["name"]
                user_id = result["id"]
                print(f"Main - User recognized: {wake_word} (ID: {user_id}). Initiating speech recognition...")
                ui.show_message(f"Welcome back, {wake_word}.\nPlease provide voice confirmation....", "white")

                speech_detected = SR.speechRecognition(wake_word)

                if speech_detected:
                    print(f"Main - Wake word '{wake_word}' detected. Sending MQTT {ACTION} request...")
                    response_payload = None

                    request_payload = {
                        "employee_id": user_id,
                        "action": ACTION,
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                    }

                    client.publish(MQTT_TOPIC_REQUEST, json.dumps(request_payload))

                    timeout = time.time() + 5
                    while time.time() < timeout and response_payload is None:
                        time.sleep(0.1)

                    if response_payload:
                        status = response_payload.get("status")

                        if status == "success":
                            msg = f"[Access Granted] {ACTION.replace('_', ' ').capitalize()} confirmed."
                            print(msg)
                            if MODE == "entry":
                                ui.show_message("ACCESS GRANTED\nWelcome!", "green")
                            else:
                                ui.show_message("ACCESS GRANTED\nGoodbye!", "green")
                            AF.play_success_message()

                            AF.play_success_message()

                        elif status == "denied":
                            reason = response_payload.get("message", "Access denied.")
                            print(f"[Access Denied] {reason} Please try again.")
                            ui.show_message(f"ACCESS DENIED\n{reason}", "red")
                            AF.play_denied_message()

                        elif status == "error":
                            reason = response_payload.get("message", "An error occurred during verification.")
                            print(f"[Error] {reason}")
                            ui.show_message(f"ERROR\n{reason}", "red")
                            AF.play_error_message()

                        else:
                            print(f"[Error] MQTT - Unexpected status: {status}")
                            ui.show_message("ERROR\nUnexpected status from server.", "red")
                            AF.play_error_message()
                    else:
                        print("[Error] MQTT - No response received. Access denied.")
                        ui.show_message("ERROR\nNo response from server.", "red")
                        AF.play_error_message()
                else:
                    print("[Access Denied] Password not recognised. Please try again.")
                    ui.show_message("ACCESS DENIED\nPassword not recognised.", "red")
                    AF.play_denied_message()
            else:
                print("[Access Denied] Face not recognised. Please try again.")
                ui.show_message("ACCESS DENIED\nFace not recognised.", "red")
                AF.play_denied_message()
        else:
            print("Main - No object detected within 100 cm. Skipping recognition cycle.")
            if screen_on:
                ui.hide_ui()
                screen_on = False

        time.sleep(2)



if __name__ == "__main__":
    main()
