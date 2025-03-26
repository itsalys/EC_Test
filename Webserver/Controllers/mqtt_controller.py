import json
import threading
import time
import base64
from Utils.mqtt_client import publish_message, register_mqtt_callback

# In-memory storage for scanned devices
device_responses = {}
device_lock = threading.Lock()


# Called once at app start to register listeners
def initialise_device_mqtt_handlers():
    register_mqtt_callback("app/get_device/response/+", handle_device_scan_response)
    register_mqtt_callback("app/update_device/+/response", handle_device_update_response)


def handle_device_scan_response(topic, payload):
    try:
        hostname = topic.split("/")[-1]
        with device_lock:
            device_responses[hostname] = {
                "hostname": hostname,
                "ip": payload.get("ip_address"),
                "mode": payload.get("mode")
            }
    except Exception as e:
        print(f"❌ Failed to process device scan response: {e}")


def handle_device_update_response(topic, payload):
    hostname = topic.split("/")[-2]
    with device_lock:
        if hostname in device_responses:
            device_responses[hostname]["update_status"] = payload.get("status", "unknown")


def mqtt_scan_devices():
    with device_lock:
        device_responses.clear()
    publish_message("app/get_device/request", {})
    time.sleep(3)  # Allow devices to respond


def get_latest_device_responses():
    with device_lock:
        return list(device_responses.values())


def mqtt_update_device_mode(hostname, mode):
    topic = f"app/update_device/{hostname}/request"
    payload = {"mode": mode}
    publish_message(topic, payload)

    # Wait for device to respond
    for _ in range(10):  # wait up to 5 seconds
        time.sleep(0.5)
        with device_lock:
            device = device_responses.get(hostname)
            if device and device.get("update_status") == "success":
                return True
            elif device and device.get("update_status") == "failed":
                return False

    return False


# Publish new employee info to edge devices
def publish_new_employee(employee):
    payload = {
        "employee_id": employee.employee_id,
        "full_name": employee.full_name,
        "profile_pic": base64.b64encode(employee.profile_pic).decode("utf-8") if employee.profile_pic else None
    }
    publish_message("app/add_employee/request", payload)