"""Application entry point.

This script creates and runs the Flask application in development mode.
For production deployment, use a WSGI server like Gunicorn instead.
"""

from app import create_app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])
