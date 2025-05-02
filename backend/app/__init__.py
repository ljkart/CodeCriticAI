"""Entry point of the Flask app.

This module initializes the application, sets up database
connections, JWT authentication, and registers all blueprints.
"""

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()


def create_app(test_config: dict | None = None) -> Flask:
    """Create and configure the Flask application.

    Args:
        test_config: Optional dictionary containing test configuration.
                    If None, production config will be used.

    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(__name__, instance_relative_config=True)

    # Enable CORS for all routes
    CORS(app)

    # Load the appropriate configuration
    if test_config is None:
        app.config.from_object("app.config")
    else:
        app.config.from_mapping(test_config)

    # Initialize Flask extensions
    db.init_app(app)
    jwt.init_app(app)

    from app.auth.routes import auth_bp
    from app.review.routes import review_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(review_bp, url_prefix="/api/review")

    @app.route("/")
    def home() -> dict:
        """Health check endpoint.

        Returns:
            dict: Simple welcome message indicating API is running.
        """
        return {"message": "Welcome to Code Reviewer Agent API"}

    return app
