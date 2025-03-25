from flask import Blueprint, render_template, request, jsonify
from Utils.auth import verify_token
from Controllers.mqtt_controller import request_device_list

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
def trigger_device_scan():
    admin, error = verify_token("admin")
    if error:
        return error

    from Controllers.mqtt_controller import trigger_device_scan
    trigger_device_scan()
    return jsonify({"message": "Device scan initiated"}), 200


