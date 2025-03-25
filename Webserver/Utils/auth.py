import jwt
import datetime
import os
from flask import request, jsonify
from Models.admin import Admin
from Models.employee import Employee
from dotenv import load_dotenv

load_dotenv()  # Load SECRET_KEY from .env

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in .env file")

# Function to generate JWT token
def generate_jwt(user_id, role):
    """Generates a JWT token for authentication."""
    payload = {
        "id": user_id,
        "role": role,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# Function to verify JWT token and return user
def verify_token(required_role):
    print("📌 Received Headers:", request.headers)  # ✅ Debugging

    token = request.headers.get("Authorization")
    print("📌 Received Authorization Header:", token)  # ✅ Debugging

    if not token:
        print("❌ No Authorization header received!")
        return None, {"error": "Unauthorized. Missing token"}

    try:
        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        print("📌 Extracted Token:", token)  # ✅ Debug log

        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        print("✅ Decoded Token:", decoded)  # ✅ Debug log

        if decoded["role"] != required_role:
            print(f"❌ Unauthorized. {required_role} access required.")
            return None, {"error": f"Unauthorized. {required_role} access required"}, 403

        return Admin.query.get(decoded["id"]) if required_role == "admin" else Employee.query.get(decoded["id"]), None

    except jwt.ExpiredSignatureError:
        print("❌ Token Expired")
        return None, {"error": "Token has expired"}

    except jwt.InvalidTokenError as e:
        print(f"❌ Invalid Token Error: {e}")
        return None, {"error": "Invalid token"}

