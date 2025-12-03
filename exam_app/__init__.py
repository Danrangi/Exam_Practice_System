from flask import Flask, g, session
from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy db instance (will be initialized in create_app)
db = SQLAlchemy()


def create_app():
    """Application factory: create and configure the Flask app."""
    app = Flask(__name__, template_folder='templates', static_folder='static')
    # Load configuration from top-level config.py
    app.config.from_object('config.Config')

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.admin import admin_bp
    from .routes.main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)

    @app.before_request
    def before_request():
        """Set g.user for request-level user info (mirrors previous behavior)."""
        g.user = None
        if 'username' in session:
            g.user = session['username']

    @app.context_processor
    def inject_admin_username():
        """Make `admin_username` available to all templates."""
        return dict(admin_username=app.config.get('ADMIN_USERNAME'))

    # Ensure database tables exist and initial data is present
    with app.app_context():
        from . import models  # noqa: F401 (ensure models are registered)
        db.create_all()
        # Add initial exam data if missing
        try:
            models.add_initial_data()
        except Exception:
            # If something goes wrong, we don't want app import to fail
            pass

    return app
