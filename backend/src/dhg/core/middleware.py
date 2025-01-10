from flask import jsonify
from werkzeug.exceptions import HTTPException


# Define our own APIError for consistency
class APIError(Exception):
    """Custom API Error class"""

    def __init__(self, message="API Error", status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


def error_handler(error):
    """Global error handler for the application."""
    if isinstance(error, APIError):
        return jsonify(
            {"error": "Database Error", "message": str(error)}
        ), error.status_code
    elif isinstance(error, HTTPException):
        return jsonify({"error": error.name, "message": error.description}), error.code
    else:
        return jsonify({"error": "Internal Server Error", "message": str(error)}), 500
