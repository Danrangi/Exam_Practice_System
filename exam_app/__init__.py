import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

# Initialize database and CSRF globally
db = SQLAlchemy()
csrf = CSRFProtect()

def create_app(test_config=None):
    # Determine the project root for finding templates/static folders
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    app = Flask(
        'exam_app',
        instance_relative_config=True,
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
