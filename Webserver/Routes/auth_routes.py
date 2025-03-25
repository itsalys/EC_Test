from flask import jsonify, Blueprint, request, render_template, redirect, url_for, session
from Controllers.auth_controller import authenticate_admin, authenticate_employee
from Utils.auth import verify_token


auth_bp = Blueprint("auth", __name__)

# Admin Login Route
@auth_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        return render_template("admin_login.html")  # ✅ Now supports GET requests

    data = request.get_json()  # ✅ Handle JSON POST request

    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Missing email or password"}), 400

    token, error = authenticate_admin(data["email"], data["password"])
    if error:
        return jsonify({"error": error}), 401

    # Store token in session (optional)
    session["token"] = token
    session["role"] = "admin"
    print("✅ Login Successful. Token:", token)

    return jsonify({"token": f"Bearer {token}"})  # ✅ JSON response for authentication


# Employee login
@auth_bp.route("/employee/login", methods=["GET", "POST"])
def employee_login():
    if request.method == "GET":
        return render_template("employee_login.html")  # ✅ Now supports GET requests
    
    data = request.get_json()

    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Missing email or password"}), 400

    token, error = authenticate_employee(data["email"], data["password"])
    if error:
        return jsonify({"error": error}), 401
    
        # Store token in session (optional)
    session["token"] = token
    session["role"] = "employee"
    print("✅ Login Successful. Token:", token)
    
    return jsonify({"token": f"Bearer {token}"})

# Verify Admin
@auth_bp.route("/admin/verify", methods=["GET"])
def verify_admin():
    admin, error = verify_token("admin")

    if error:
        print(f"❌ Authentication failed: {error}")  # ✅ Debugging
        return jsonify({"error": "Unauthorized"}), 401

    if not admin:
        print("❌ Admin not found in database!")
        return jsonify({"error": "Admin not found"}), 404

    return jsonify({"message": "Token valid", "admin": admin.admin_id})  # ✅ Use `admin.admin_id`

# Verify Employee
@auth_bp.route("/employee/verify", methods=["GET"])
def verify_employee():
    employee, error = verify_token("employee")

    if error:
        print(f"❌ Authentication failed: {error}")  # ✅ Debugging
        return jsonify({"error": "Unauthorized"}), 401

    if not employee:
        print("❌ Employee not found in database!")
        return jsonify({"error": "Employee not found"}), 404

    return jsonify({"message": "Token valid", "employee": employee.employee_id})
