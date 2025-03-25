from Models.embedding import Embedding
from Models import db

def get_all_embeddings():
    """Retrieve all embeddings."""
    embeddings = Embedding.query.all()
    return [
        {
            "embedding_id": emb.embedding_id,
            "employee_id": emb.employee_id,
            "vector": emb.vector
        }
        for emb in embeddings
    ]

def get_employee_embedding(employee_id):
    """Retrieve embedding for a specific employee."""
    embedding = Embedding.query.filter_by(employee_id=employee_id).first()
    
    if not embedding:
        return None, "No embedding found for this employee"

    return {
        "embedding_id": embedding.embedding_id,
        "employee_id": embedding.employee_id,
        "vector": embedding.vector
    }, None

def add_embedding(data):
    """Add a new face embedding."""
    new_embedding = Embedding(
        employee_id=data["employee_id"],
        vector=data["vector"]  # Store as a string (JSON or comma-separated values)
    )

    db.session.add(new_embedding)
    db.session.commit()
    return "Embedding added successfully", None

def update_embedding(employee_id, data):
    """Update an existing embedding for an employee."""
    embedding = Embedding.query.filter_by(employee_id=employee_id).first()
    if not embedding:
        return None, "No embedding found for this employee"

    embedding.vector = data["vector"]
    db.session.commit()
    return "Embedding updated successfully", None
