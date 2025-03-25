import base64
from Utils.mqtt_client import publish_message, register_mqtt_callback, reconnect_subscriber
import threading

# === ADD EMPLOYEE MQTT ===

def publish_new_employee(employee):
    payload = {
        "employee_id": employee.employee_id,
        "full_name": employee.full_name,
        "profile_pic": base64.b64encode(employee.profile_pic).decode("utf-8") if employee.profile_pic else None
    }
    publish_message("app/add_employee/request", payload)


# === DEVICE MANAGEMENT MQTT ===

_device_response_cache = {}
_lock = threading.Lock()

def trigger_device_scan():
    with _lock:
        _device_response_cache.clear()

    reconnect_subscriber()  # Blocks until reconnected or timeout
    publish_message("app/device_management/request", {})


def _device_response_handler(topic, payload):
    hostname = payload.get("hostname")
    if hostname:
        with _lock:
            _device_response_cache[hostname] = payload
        print(f"Cached response from {hostname}")

register_mqtt_callback("app/device_management/response/+", _device_response_handler)

def request_device_list():
    with _lock:
        print(f"🔍 Cache size: {len(_device_response_cache)}")
        if not _device_response_cache:
            return None, "No response received from devices."
        return list(_device_response_cache.values()), None

def publish_update_device_mode(hostname, mode):
    payload = {"mode": mode}
    topic = f"app/update_device/{hostname}/request"
    publish_message(topic, payload)
