from Models import db

class Embedding(db.Model):
    __tablename__ = "embedding"

    embedding_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.employee_id"), nullable=False)
    vector = db.Column(db.String(255), nullable=False)
    
    # Relationship with Employee
    employee = db.relationship("Employee", backref="embeddings")

    def __repr__(self):
        return f"<Embedding {self.embedding_id} - Employee {self.employee_id}>"
