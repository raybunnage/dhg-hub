from flask import Flask
from flask.cli import load_dotenv
import os
from dhg.core.config import config


def create_app(config_name=None):
    """Create and configure the Flask application."""
    load_dotenv()

    app = Flask(__name__)

    # Configure the app
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app.config.from_object(config[config_name])

    # Register CLI commands including test command
    from dhg.cli import register_commands

    register_commands(app)

    # Optional: Print debug info
    app.logger.info(f"Created app with config: {config_name}")
    app.logger.info(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")

    return app
