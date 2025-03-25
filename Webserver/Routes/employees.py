from flask import Blueprint, redirect, request, jsonify, render_template, url_for, send_file
from Controllers.employee_controller import (
    get_all_employees,
    get_employee_by_id,
    add_employee,
    update_employee,
    delete_employee,
    update_employee_profile_picture,
    change_employee_password
)
import base64
from Utils.auth import verify_token
from Models.employee import Employee

employees_bp = Blueprint("employees", __name__)

@employees_bp.route("/list", methods=["GET"])
def employee_list_page():
    return render_template("employee_list.html", role="admin")

# Admin: Get all employees
@employees_bp.route("/", methods=["GET"])
def get_employees():
    admin, error = verify_token("admin")  
    if error:
        return error

    employees = get_all_employees()
    return jsonify(employees)

@employees_bp.route("/<int:employee_id>/profile_pic", methods=["GET"])
def get_profile_picture(employee_id):
    employee = Employee.query.get(employee_id)
    if not employee or not employee.profile_pic:
        return jsonify({"error": "No profile picture available"}), 404

    image_data = base64.b64encode(employee.profile_pic).decode("utf-8")
    return jsonify({"profile_pic": image_data})


# Route for updating profile picture
@employees_bp.route("/<int:employee_id>/profile_pic", methods=["POST"])
def update_profile_picture(employee_id):
    admin, error = verify_token("admin")  
    if error:
        return error  # Return authentication error

    if "profile_pic" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["profile_pic"]
    message, error = update_employee_profile_picture(employee_id, file)

    if error:
        return jsonify({"error": error}), 404

    return jsonify({"message": message})

@employees_bp.route("/<int:employee_id>/profile", methods=["GET"])
def employee_profile_page(employee_id):
    
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
    
    return render_template("employee_profile.html", employee=employee, role="admin")

# Employee: View Profile Page
@employees_bp.route("/myprofile", methods=["GET"])
def employee_view_profile_page():
    return render_template("employee_view_profile.html", role="employee")

# Employee/Admin: Get employee by ID
@employees_bp.route("/<int:employee_id>", methods=["GET"])
def get_employee(employee_id):
    # user, error = verify_token("admin")  
    # if error:
    #     user, error = verify_token("employee")  
    #     if error or user.employee_id != employee_id:
    #         return jsonify({"error": "Unauthorized access"}), 403

    employee, error = get_employee_by_id(employee_id)
    if error:
        return jsonify({"error": error}), 404

    return jsonify(employee)

# Serve the Add Employee page
@employees_bp.route("/add", methods=["GET"])
def add_employee_page():   
    return render_template("add_employee.html", role="admin")

# Admin: Add a new employee
@employees_bp.route("/", methods=["POST"])
def create_employee():
    admin, error = verify_token("admin")  
    if error:
        return jsonify({"error": "Unauthorized. Admin access required"}), 403
    
    full_name = request.form.get("full_name")
    department = request.form.get("department")
    email = request.form.get("email")
    password = request.form.get("password")
    profile_pic = request.files.get("profile_pic")

    if not all([full_name, department, email, password]):
        return jsonify({"error": "Missing required fields"}), 400

    profile_pic_data = profile_pic.read() if profile_pic else None

    data = {
        "full_name": full_name,
        "department": department,
        "email": email,
        "password": password,
        "profile_pic": profile_pic_data
    }

    message, error = add_employee(data)  # Call the controller function

    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": message}), 201

# Admin: Update employee details
@employees_bp.route("/<int:employee_id>", methods=["PUT"])
def modify_employee(employee_id):
    admin, error = verify_token("admin")  
    if error:
        return error

    data = request.get_json()
    message, error = update_employee(employee_id, data)

    if error:
        return jsonify({"error": error}), 404

    return jsonify({"message": message})

# Admin: Delete an employee
@employees_bp.route("/<int:employee_id>", methods=["DELETE"])
def remove_employee(employee_id):
    admin, error = verify_token("admin")  
    if error:
        return error

    message, error = delete_employee(employee_id)

    if error:
        return jsonify({"error": error}), 404

    return jsonify({"message": message})

# Employee: Change Password
@employees_bp.route("/<int:employee_id>/change_password", methods=["PUT"])
def change_password(employee_id):
    user, error = verify_token("employee")  
    if error or user.employee_id != employee_id:
        return jsonify({"error": "Unauthorized access"}), 403

    data = request.get_json()
    current_password = data.get("current_password")
    new_password = data.get("new_password")

    # Validate input
    if not all([current_password, new_password]):
        return jsonify({"error": "Missing required fields"}), 400

    # Call the controller function
    message, error = change_employee_password(employee_id, current_password, new_password)

    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": message})