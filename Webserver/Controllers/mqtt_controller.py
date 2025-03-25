import base64
import threading
import time
from Utils.mqtt_client import (
    publish_message,
    register_mqtt_callback,
    reconnect_subscriber
)

_device_response_cache = {}
_confirmation_flags = {}
_lock = threading.Lock()

def publish_new_employee(employee):
    payload = {
        "employee_id": employee.employee_id,
        "full_name": employee.full_name,
        "profile_pic": base64.b64encode(employee.profile_pic).decode("utf-8") if employee.profile_pic else None
    }
    publish_message("app/add_employee/request", payload)

def trigger_device_scan():
    with _lock:
        _device_response_cache.clear()
    reconnect_subscriber()
    publish_message("app/device_management/request", {})

def _device_response_handler(topic, payload):
    hostname = payload.get("hostname")
    if hostname:
        with _lock:
            _device_response_cache[hostname] = payload

register_mqtt_callback("app/device_management/response/+", _device_response_handler)

def request_device_list():
    with _lock:
        if not _device_response_cache:
            return None, "No response received from devices."
        return list(_device_response_cache.values()), None

def publish_device_mode_update(hostname, mode):
    topic = f"app/update_device/{hostname}"
    payload = {"mode": mode}
    publish_message(topic, payload)

def _device_mode_confirm_handler(topic, payload):
    hostname = topic.split("/")[-1]
    with _lock:
        _confirmation_flags[hostname] = True

register_mqtt_callback("app/update_device/confirm/+", _device_mode_confirm_handler)

def wait_for_mode_confirmation(hostname, timeout=3):
    start = time.time()
    while time.time() - start < timeout:
        with _lock:
            if _confirmation_flags.pop(hostname, None):
                return True
        time.sleep(0.2)
    return False
