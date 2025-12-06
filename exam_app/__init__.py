import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

# Initialize database and CSRF globally
db = SQLAlchemy()
csrf = CSRFProtect()

def create_app(test_config=None):
    # Check if we are running as a compiled .exe (Frozen)
    if getattr(sys, 'frozen', False):
        # 1. TEMPLATES/STATIC: Look inside the temporary bundled folder
        project_root = sys._MEIPASS
        
        # 2. DATABASE: Look in the same folder as the .exe (so data is saved permanently)
        # We explicitly set the 'instance_path' to the executable's directory
        exe_dir = os.path.dirname(sys.executable)
        instance_path = os.path.join(exe_dir, 'instance')
        
        # Create the instance folder if it doesn't exist
        if not os.path.exists(instance_path):
            os.makedirs(instance_path)
            
    else:
        # Running normally with 'python app.py'
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        instance_path = None # Flask handles this automatically

    app = Flask(
        'exam_app',
        instance_relative_config=True,
        instance_path=instance_path, # <--- This ensures the DB is saved correctly
        template_folder=os.path.join(project_root, 'templates'), 
        static_folder=os.path.join(project_root, 'static')
    )

    # Load configuration
    from . import config
    app.config.from_object(config.Config)

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        # Import models and utility functions so they are registered
        from . import models
        from . import utils
        
        # Create database tables if they don't exist
        db.create_all()
        utils.add_initial_data(app)

        # Register Blueprints for routes
        from .routes import auth, admin, main
        app.register_blueprint(auth.bp)
        app.register_blueprint(admin.bp)
        app.register_blueprint(main.bp)

        # Ensure before_request is registered
        app.before_request(utils.before_request)
        
        return app
