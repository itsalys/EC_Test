from flask import Blueprint

# Import blueprints from route files
from Routes.employees import employees_bp
from Routes.attendance import attendance_bp
from Routes.embedding import embedding_bp
from Routes.auth_routes import auth_bp
from Routes.devices import devices_bp

# Blueprint registration
def register_routes(app):
    app.register_blueprint(employees_bp, url_prefix="/employees")
    app.register_blueprint(attendance_bp, url_prefix="/attendance")
    app.register_blueprint(embedding_bp, url_prefix="/embedding")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(devices_bp, url_prefix="/devices")
