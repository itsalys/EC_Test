from flask import Blueprint, request, jsonify, render_template
from Models.attendance import Attendance
from Models.employee import Employee
from Models import db
from Utils.auth import verify_token
from Controllers.attendance_controller import (
    get_all_attendance,
    get_employee_attendance,
    update_attendance_record,
    add_attendance_record
)
from sqlalchemy import func
from datetime import datetime

attendance_bp = Blueprint("attendance", __name__)

@attendance_bp.route("/list", methods=["GET"])
def attendance_list_page():
    """Serve the Attendance List page"""
    return render_template("attendance_list.html", role="admin")

# Get all attendance records
@attendance_bp.route("/", methods=["GET"])
def fetch_attendance():
    """Admin: Get all attendance records"""
    admin, error = verify_token("admin")
    if error:
        return error

    records = get_all_attendance()
    return jsonify(records)

@attendance_bp.route("/<int:employee_id>", methods=["GET"])
def fetch_employee_attendance(employee_id):
    """Admin: Get an employee's attendance records"""
    admin, error = verify_token("admin")
    if error:
        return error

    response = get_employee_attendance(employee_id)
    return response
    
# Add an attendance record
@attendance_bp.route("/", methods=["POST"])
def add_attendance():
    """Route for adding an attendance record (Clock In / Clock Out)"""
    admin, error = verify_token("admin")  # ✅ Ensure admin authentication
    if error:
        return error

    data = request.get_json()
    message, error = add_attendance_record(data)

    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": message}), 201

# Employee: Dashboard Page
@attendance_bp.route("/dashboard", methods=["GET"])
def employee_dashboard_page():
    return render_template("employee_dashboard.html", role="employee")

# Employee: Get their own attendance records (Requires JWT)
@attendance_bp.route("/me", methods=["GET"])
def get_my_attendance():
    print("📌 Received Authorization Header:", request.headers.get("Authorization"))
    employee, error = verify_token("employee")
    if error:
        return jsonify({"error": "Unauthorized"}), 401  # Return JSON error message if authentication fails

    records = Attendance.query.filter_by(employee_id=employee.employee_id).all()
    
    today = datetime.now().date()

    latest_record = Attendance.query.filter(Attendance.employee_id == employee.employee_id).order_by(Attendance.timestamp.desc()).first()

    # Determine the current status (clocked in or out)
    if latest_record:
        if latest_record.clocked_in == 1:
            current_status = "clocked_in"
        else:
            current_status = "clocked_out"
    else:
        current_status = "not_clocked_in"  # No records found for the employee

    return jsonify({
        "attendance_records": [
            {
                "attendance_id": rec.attendance_id,
                "timestamp": rec.timestamp.isoformat(),
                "clocked_in": rec.clocked_in
            } for rec in records
        ],
        "current_status": current_status
    })


    
# Admin: Update an employee's clock-in status and timestamp
@attendance_bp.route("/<int:attendance_id>", methods=["PUT"])
def update_attendance(attendance_id):
    """Admin: Update an existing attendance record"""
    admin, error = verify_token("admin")
    if error:
        return error

    data = request.get_json()
    message, error = update_attendance_record(attendance_id, data)

    if error:
        return jsonify({"error": error}), 404

    return jsonify({"message": message})
