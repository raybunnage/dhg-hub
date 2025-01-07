from typing import List
from dataclasses import dataclass


@dataclass
class APIError(Exception):
    """Base API error."""

    message: str
    code: int = 400


def handle_multiple_errors(errors: List[Exception]) -> None:
    """Handle multiple errors using exception groups."""
    if errors:
        raise ExceptionGroup("Multiple errors occurred", errors)
