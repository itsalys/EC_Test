import pytz
from Models.attendance import Attendance
from Models.employee import Employee
from Models import db
from datetime import datetime, timezone, date

LOCAL_TZ = pytz.timezone("Asia/Singapore")  # Change this to your timezone

def get_all_attendance():
    """Retrieve all attendance records."""
    records = (
        db.session.query(
            Attendance.attendance_id,
            Attendance.employee_id,
            Attendance.timestamp,
            Attendance.clocked_in,
            Employee.full_name  # Join Employee Name
        )
        .join(Employee, Employee.employee_id == Attendance.employee_id)
        .order_by(Attendance.timestamp.desc())
        .all()
    )
    
    return [
        {
            "id": rec.attendance_id,
            "employee_id": rec.employee_id,
            "name": rec.full_name,
            "timestamp": rec.timestamp.isoformat(),
            "clocked_in": rec.clocked_in
        }
        for rec in records
    ]

def get_employee_attendance(employee_id):
    """Retrieve attendance records for a specific employee."""
    records = (
        db.session.query(
            Attendance.attendance_id,
            Attendance.employee_id,
            Attendance.timestamp,
            Attendance.clocked_in,
            Employee.full_name
        )
        .join(Employee, Employee.employee_id == Attendance.employee_id)
        .filter(Attendance.employee_id == employee_id)
        .order_by(Attendance.timestamp.desc())  # Sort by timestamp DESC
        .all()
    )
    if not records:
        return None, "No attendance records found"

    return [
        {
            "id": rec.attendance_id,
            "employee_id": rec.employee_id,
            "name": rec.full_name,
            "timestamp": rec.timestamp.isoformat(),
            "clocked_in": rec.clocked_in
        }
        for rec in records
    ], None

def add_attendance_record(data):
    """Add a new attendance record for an employee (Clock In / Clock Out)."""
    if "employee_id" not in data or "clocked_in" not in data:
        return None, "Missing required fields: employee_id, clocked_in"

    employee = Employee.query.get(data["employee_id"])
    if not employee:
        return None, "Employee not found"

    clocked_in = bool(data["clocked_in"])
    today = datetime.now(LOCAL_TZ).date()

    # Ensure timestamp is properly formatted
    timestamp = data.get("timestamp")
    if timestamp:
        try:
            timestamp = datetime.fromisoformat(timestamp)  # Convert from string
            timestamp = LOCAL_TZ.localize(timestamp) if timestamp.tzinfo is None else timestamp.astimezone(LOCAL_TZ)

        except ValueError:
            return None, "Invalid timestamp format. Use ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"
    else:
        timestamp = datetime.now(LOCAL_TZ)  

    # Create a new attendance entry
    new_record = Attendance(
        employee_id=data["employee_id"],
        clocked_in=clocked_in,
        timestamp=timestamp
    )
    db.session.add(new_record)
    db.session.commit()

    return f"{'Clock-in' if clocked_in else 'Clock-out'} recorded successfully", None


def update_attendance_record(attendance_id, data):
    """Update an existing attendance record."""
    record = Attendance.query.get(attendance_id)
    if not record:
        return None, "Attendance record not found"

    if "clocked_in" in data:
        record.clocked_in = bool(data["clocked_in"])

    if "timestamp" in data:
        try:
            record.timestamp = datetime.fromisoformat(data["timestamp"])
        except ValueError:
            return None, "Invalid timestamp format. Use ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"

    db.session.commit()
    return "Attendance record updated successfully", None
