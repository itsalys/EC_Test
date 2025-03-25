from Utils.mqtt_client import publish_message, register_mqtt_callback, reconnect_subscriber
import base64
import threading
import time


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

_response_events = {}
_response_payloads = {}
_response_lock = threading.Lock()


def publish_update_device_mode(hostname, mode, timeout=5):
    response_topic = f"app/update_device/{hostname}/response"
    request_topic = f"app/update_device/{hostname}/request"

    event = threading.Event()

    def _response_callback(topic, payload):
        with _response_lock:
            _response_payloads[hostname] = payload
            event.set()

    # Temporarily register a handler for the specific response
    register_mqtt_callback(response_topic, _response_callback)

    payload = {"mode": mode}
    publish_message(request_topic, payload)

    # Wait for response
    success = event.wait(timeout=timeout)
    if success:
        return _response_payloads.get(hostname), None
    else:
        return None, f"No response from device '{hostname}' within {timeout} seconds."
