from flask import Blueprint, jsonify, request, render_template
from Controllers.mqtt_controller import (
    mqtt_scan_devices,
    mqtt_update_device_mode,
    get_latest_device_responses
)


# Blueprint for device routes
devices_bp = Blueprint("devices", __name__)


@devices_bp.route("/list", methods=["GET"])
def device_list_page():
    return render_template("device_management.html", role="admin")


@devices_bp.route("/scan", methods=["GET"])
def scan_devices():
    mqtt_scan_devices()
    devices = get_latest_device_responses()
    return jsonify({"devices": devices})


@devices_bp.route("/update_mode/<string:hostname>", methods=["POST"])
def update_device_mode(hostname):
    data = request.get_json()
    mode = data.get("mode")

    if mode not in ["entry", "exit"]:
        return jsonify({"success": False, "error": "Invalid mode"}), 400

    success = mqtt_update_device_mode(hostname, mode)

    if success:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Device did not respond or failed"}), 500
