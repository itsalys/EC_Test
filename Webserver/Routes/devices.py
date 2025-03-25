from flask import Blueprint, render_template, request, jsonify
from Utils.auth import verify_token
from Controllers.mqtt_controller import publish_update_device_mode

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


# @devices_bp.route("/update_mode", methods=["POST"])
# def update_mode():
#     admin, error = verify_token("admin")
#     if error:
#         return error

#     data = request.get_json()
#     hostname = data.get("hostname")
#     mode = data.get("mode")

#     if not hostname or mode not in ["entry", "exit"]:
#         return jsonify({"error": "Invalid payload"}), 400

#     from Controllers.mqtt_controller import publish_update_device_mode
#     publish_update_device_mode(hostname, mode)
#     return jsonify({"message": "Mode update sent"})

from Controllers.mqtt_controller import publish_update_device_mode

@devices_bp.route("/update_mode", methods=["POST"])
def update_mode():
    admin, error = verify_token("admin")
    if error:
        return error

    data = request.get_json()
    hostname = data.get("hostname")
    mode = data.get("mode")

    if not hostname or mode not in ["entry", "exit"]:
        return jsonify({"error": "Invalid payload"}), 400

    response, err = publish_update_device_mode(hostname, mode)
    if err:
        return jsonify({"error": err}), 504  # Gateway Timeout

    return jsonify(response)
