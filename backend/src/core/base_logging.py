from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from functools import wraps
import logging
from datetime import datetime
import time
import inspect
from pathlib import Path
import os


class LoggerInterface(ABC):
    @abstractmethod
    def debug(self, message: str) -> None:
        pass

    @abstractmethod
    def info(self, message: str) -> None:
        pass

    @abstractmethod
    def warning(self, message: str) -> None:
        pass

    @abstractmethod
    def error(self, message: str, error: Exception = None) -> None:
        pass

    @abstractmethod
    def critical(self, message: str, error: Exception = None) -> None:
        pass

    @abstractmethod
    def exception(self, message: str) -> None:
        """Log exception info with ERROR level (should only be called from an except block)"""
        pass

    @abstractmethod
    def set_level(self, level: int) -> None:
        """Set the logging level"""
        pass

    @abstractmethod
    def get_level(self) -> int:
        """Get the current logging level"""
        pass

    @abstractmethod
    def log_method_call(
        self,
        method_name: str,
        args: tuple,
        kwargs: Dict[str, Any],
        duration: float,
        result: Any = None,
        error: Exception = None,
    ) -> None:
        """Log method entry/exit with parameters and results"""
        pass

    @abstractmethod
    def add_context(self, **kwargs) -> None:
        """Add context information to all subsequent log messages"""
        pass

    @abstractmethod
    def clear_context(self) -> None:
        """Clear any stored context information"""
        pass

    @abstractmethod
    def log_basic_call(
        self,
        method_name: str,
        result: Any = None,
        error: Exception = None,
    ) -> None:
        """Log basic method entry/exit with results"""
        pass


class Logger(LoggerInterface):
    def __init__(self, name: str = __name__):
        self._logger = logging.getLogger(name)

        # Determine log directory based on environment
        if os.name == "posix":  # Linux/Unix
            self._log_dir = Path("/var/log/dhg-hub")
        else:  # Windows
            self._log_dir = (
                Path(os.environ.get("PROGRAMDATA", "C:\\ProgramData"))
                / "dhg-hub"
                / "logs"
            )

        # Ensure log directory exists and has correct permissions
        try:
            self._log_dir.mkdir(parents=True, exist_ok=True)
            if os.name == "posix":
                # Set proper permissions on Unix systems
                os.chmod(self._log_dir, 0o755)
        except PermissionError:
            # Fallback to user's home directory if we don't have permission
            self._log_dir = Path.home() / ".your_app_name" / "logs"
            self._log_dir.mkdir(parents=True, exist_ok=True)

        # Configure console handler
        console_handler = logging.StreamHandler()
        self._formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(self._formatter)
        self._logger.addHandler(console_handler)

        # Configure file handler
        log_file = self._log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(self._formatter)
        self._logger.addHandler(file_handler)

        self._logger.setLevel(logging.INFO)
        self._context = {}
        self._formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(context)s - %(message)s"
        )

    @property
    def logger(self):
        """Access the internal logger instance"""
        return self._logger

    def debug(self, message: str) -> None:
        self._logger.debug(message)

    def info(self, message: str) -> None:
        self._logger.info(message)

    def warning(self, message: str) -> None:
        self._logger.warning(message)

    def error(self, message: str, error: Exception = None) -> None:
        self._logger.error(message, exc_info=error if error else True)

    def critical(self, message: str, error: Exception = None) -> None:
        self._logger.critical(message, exc_info=error if error else True)

    def exception(self, message: str) -> None:
        self._logger.exception(message)

    def set_level(self, level: int) -> None:
        self._logger.setLevel(level)

    def get_level(self) -> int:
        return self._logger.getEffectiveLevel()

    def add_context(self, **kwargs) -> None:
        self._context.update(kwargs)

    def clear_context(self) -> None:
        self._context.clear()

    def log_method_call(
        self,
        method_name: str,
        args: tuple,
        kwargs: Dict[str, Any],
        duration: float,
        result: Any = None,
        error: Exception = None,
    ) -> None:
        context = f"method={method_name}"
        if error:
            self._logger.error(
                f"{context} - args={args} kwargs={kwargs} duration={duration:.3f}s - ERROR: {str(error)}",
                exc_info=error,
            )
        else:
            self._logger.debug(
                f"{context} - args={args} kwargs={kwargs} duration={duration:.3f}s - result={result}"
            )

    def log_basic_call(
        self,
        method_name: str,
        result: Any = None,
        error: Exception = None,
    ) -> None:
        if error:
            self._logger.error(
                f"method={method_name} - ERROR: {str(error)}",
                exc_info=error,
            )
        else:
            self._logger.info(f"method={method_name} - result={result}")


def log_method(logger: Optional[LoggerInterface] = None):
    """Decorator to automatically log method entry/exit with parameters and timing"""

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            method_name = func.__name__
            current_logger = logger or getattr(args[0], "_logger", None)

            if not current_logger:
                return await func(*args, **kwargs)

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                current_logger.log_method_call(
                    method_name, args, kwargs, duration, result
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                current_logger.log_method_call(
                    method_name, args, kwargs, duration, error=e
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            method_name = func.__name__
            current_logger = logger or getattr(args[0], "_logger", None)

            if not current_logger:
                return func(*args, **kwargs)

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                current_logger.log_method_call(
                    method_name, args, kwargs, duration, result
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                current_logger.log_method_call(
                    method_name, args, kwargs, duration, error=e
                )
                raise

        return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

    return decorator


def log_basic(logger=None):
    """Basic logging decorator that only logs method entry/exit and errors.

    A lightweight alternative to log_method when you don't need parameter tracing
    and timing information.

    Args:
        logger: Optional logger instance. If None, tries to get logger from instance

    Example:
        @log_basic()
        async def simple_operation(self):
            # Only logs:
            # - "Entering simple_operation"
            # - "Exiting simple_operation"
            # - Errors if they occur
    """

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            method_name = func.__name__
            current_logger = logger or getattr(args[0], "_logger", None)

            if not current_logger:
                return await func(*args, **kwargs)

            try:
                current_logger.debug(f"Entering {method_name}")
                result = await func(*args, **kwargs)
                current_logger.debug(f"Exiting {method_name}")
                return result
            except Exception as e:
                current_logger.error(f"Error in {method_name}: {str(e)}")
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            method_name = func.__name__
            current_logger = logger or getattr(args[0], "_logger", None)

            if not current_logger:
                return func(*args, **kwargs)

            try:
                current_logger.debug(f"Entering {method_name}")
                result = func(*args, **kwargs)
                current_logger.debug(f"Exiting {method_name}")
                return result
            except Exception as e:
                current_logger.error(f"Error in {method_name}: {str(e)}")
                raise

        return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

    return decorator
