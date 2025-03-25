from flask import Blueprint, request, jsonify
from Controllers.embedding_controller import (
    get_all_embeddings,
    get_employee_embedding,
    add_embedding,
    update_embedding
)
from Utils.auth import verify_token  # ✅ Protect routes

embedding_bp = Blueprint("embedding", __name__)

# Admin: Get all embeddings
@embedding_bp.route("/", methods=["GET"])
def fetch_embeddings():
    admin, error = verify_token("admin")  # ✅ Only admins can view all embeddings
    if error:
        return error

    embeddings = get_all_embeddings()
    return jsonify(embeddings)

# Employee: Get their own embedding
@embedding_bp.route("/me", methods=["GET"])
def fetch_my_embedding():
    employee, error = verify_token("employee")
    if error:
        return error

    embedding, error = get_employee_embedding(employee.employee_id)
    if error:
        return jsonify({"error": error}), 404

    return jsonify(embedding)

# Admin: Get embedding for a specific employee
@embedding_bp.route("/<int:employee_id>", methods=["GET"])
def fetch_employee_embedding(employee_id):
    admin, error = verify_token("admin")
    if error:
        return error

    embedding, error = get_employee_embedding(employee_id)
    if error:
        return jsonify({"error": error}), 404

    return jsonify(embedding)

# Employee: Add embedding (Face Recognition Data)
@embedding_bp.route("/", methods=["POST"])
def record_embedding():
    employee, error = verify_token("employee")
    if error:
        return error

    data = request.get_json()
    data["employee_id"] = employee.employee_id  # Ensure correct ID
    message, error = add_embedding(data)

    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": message}), 201

# Employee: Update their embedding
@embedding_bp.route("/", methods=["PUT"])
def modify_embedding():
    employee, error = verify_token("employee") 
    if error:
        return error

    data = request.get_json()
    message, error = update_embedding(employee.employee_id, data)

    if error:
        return jsonify({"error": error}), 404

    return jsonify({"message": message})
