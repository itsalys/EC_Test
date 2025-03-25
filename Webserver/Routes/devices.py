from flask import Blueprint, render_template, request, jsonify
from Utils.auth import verify_token
from Controllers.mqtt_controller import (
    request_device_list,
    trigger_device_scan,
    publish_device_mode_update,
    wait_for_mode_confirmation
)

devices_bp = Blueprint("devices", __name__)

@devices_bp.route("/list", methods=["GET"])
def device_list_page():
    return render_template("device_management.html", role="admin")

@devices_bp.route("/", methods=["GET"])
def get_device_data():
    admin, error = verify_token("admin")
    if error:
        return error

    devices, error = request_device_list()
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"devices": devices})

@devices_bp.route("/trigger", methods=["POST"])
def trigger_device_scan_route():
    admin, error = verify_token("admin")
    if error:
        return error

    trigger_device_scan()
    return jsonify({"message": "Scan triggered"}), 200

@devices_bp.route("/<hostname>/mode", methods=["POST"])
def update_device_mode(hostname):
    admin, error = verify_token("admin")
    if error:
        return error

    data = request.get_json()
    mode = data.get("mode")
    if mode not in ["entry", "exit"]:
        return jsonify({"error": "Invalid mode"}), 400

    publish_device_mode_update(hostname, mode)
    success = wait_for_mode_confirmation(hostname)

    if success:
        return jsonify({"success": True})
    return jsonify({"error": "No confirmation received"}), 504
