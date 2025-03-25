from Utils.mqtt_client import publish_message
import base64

def publish_new_employee(employee):
    payload = {
        "employee_id": employee.employee_id,
        "full_name": employee.full_name,
        "profile_pic": base64.b64encode(employee.profile_pic).decode("utf-8") if employee.profile_pic else None
    }
    publish_message("app/add_employee/request", payload)

# Add more topic-specific functions as needed
