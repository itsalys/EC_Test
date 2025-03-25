from Models import db

class Employee(db.Model):
    __tablename__ = "employees"

    employee_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    profile_pic = db.Column(db.LargeBinary(length=(16 * 1024 * 1024)), nullable=False)  # 16 MB  # BLOB type for image
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Store hashed password

    def __repr__(self):
        return f"<Employee {self.full_name}>"
