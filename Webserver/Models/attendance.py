from Models import db

class Attendance(db.Model):
    __tablename__ = "attendance"

    attendance_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.employee_id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    clocked_in = db.Column(db.Boolean, nullable=False)

    # Relationship with Employee
    employee = db.relationship("Employee", backref="attendance_records")

    def __repr__(self):
        return f"<Attendance {self.employee_id} - {self.timestamp}>"
