import bcrypt
from Models.employee import Employee
from Models.admin import Admin
from Models import db
from Utils.auth import generate_jwt

def authenticate_admin(email, password):
    """Authenticate admin and return token if valid."""
    admin = Admin.query.filter_by(email=email).first()
    if not admin or not bcrypt.checkpw(password.encode("utf-8"), admin.password.encode("utf-8")):
        return None, "Invalid email or password"

    token = generate_jwt(admin.admin_id, "admin")
    return token, None

def authenticate_employee(email, password):
    """Authenticate employee and return token if valid."""
    employee = Employee.query.filter_by(email=email).first()
    if not employee or not bcrypt.checkpw(password.encode("utf-8"), employee.password.encode("utf-8")):
        return None, "Invalid email or password"

    token = generate_jwt(employee.employee_id, "employee")
    return token, None
