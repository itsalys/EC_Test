from flask import Flask
from Database.db_connection import db, DATABASE_URI
from Database.db_setup import init_db
from Routes import register_routes
from dotenv import load_dotenv
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, expose_headers=["Authorization"], allow_headers=["Authorization", "Content-Type"])  # ✅ Allow Authorization header


load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")


# Configure Database URI
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy
db.init_app(app)

# Ensure database exists and create tables if needed
init_db(app)

# Register routes
register_routes(app)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
