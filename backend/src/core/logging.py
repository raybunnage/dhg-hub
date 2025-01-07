import logging
from typing import Dict, Any


def setup_logging(config: Dict[str, Any]) -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=config.get("log_level", "INFO"),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
