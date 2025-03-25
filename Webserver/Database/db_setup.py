import mysql.connector
import os
from Database.db_connection import db
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

def ensure_database():
    """Check if the database exists, create it if not."""
    try:
        temp_db = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        temp_cursor = temp_db.cursor()
        
        # Check if database exists
        temp_cursor.execute(f"SHOW DATABASES LIKE '{DB_NAME}'")
        database_exists = temp_cursor.fetchone()

        if not database_exists:
            temp_cursor.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"Database '{DB_NAME}' created successfully.")

        temp_cursor.close()
        temp_db.close()
    
    except mysql.connector.Error as err:
        print(f"Error checking/creating database: {err}")

def init_db(app):
    """Ensure the database exists, then initialize SQLAlchemy tables."""
    ensure_database()  # Make sure database exists before using SQLAlchemy

    with app.app_context():
        # Import models inside the function to ensure they are registered
        from Models.employee import Employee
        from Models.attendance import Attendance
        from Models.admin import Admin
        from Models.embedding import Embedding

        db.create_all()  # Creates tables if they don't exist
        
        # Check if an admin already exists
        existing_admin = Admin.query.filter_by(email="admin@gmail.com").first()

        if not existing_admin:
            new_admin = Admin(
                email="admin@gmail.com",
                password="$2b$12$FlH5tOLvYmSCsY/7v1lD1.X4qHIzO82mBi2RSJdcoNG7pgrb8CP9K"  # Pre-hashed password
            )
            db.session.add(new_admin)
            print("Admin user created.")
        
        db.session.commit()  # Ensure changes are committed
        print("Tables initialized successfully.")
