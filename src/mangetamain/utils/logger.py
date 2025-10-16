"""Lightweight logging utility with colored console output and file handlers."""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import ClassVar


class ColoredFormatter(logging.Formatter):
    """A logging formatter that adds ANSI color codes to console output.

    This formatter applies simple ANSI color codes to the formatted
    message according to the record level name (DEBUG, INFO, WARNING,
    ERROR, CRITICAL). It improves readability when logs are viewed in
    a terminal that supports ANSI escapes.
    """

    COLORS: ClassVar[dict[str, str]] = {
        "DEBUG": "\033[0;36m",  # Cyan
        "INFO": "\033[0;32m",  # Green
        "WARNING": "\033[0;33m",  # Yellow
        "ERROR": "\033[0;31m",  # Red
        "CRITICAL": "\033[0;37m\033[41m",  # White on Red BG
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format the record and wrap it in color escape sequences.

        Args:
          record: The logging.Record to format.

        Returns:
          The formatted log string with ANSI color codes applied.
        """
        msg = (
            self.COLORS.get(record.levelname, self.COLORS["RESET"])
            + super().format(record)
            + self.COLORS["RESET"]
        )
        return msg


class BaseLogger:
    """Lightweight application logger with file and console handlers.

    BaseLogger is a small wrapper around Python's standard logging that
    configures a file handler and a console handler (with colors).
    It is implemented as a simple singleton so multiple instantiations
    return the same configured logger instance.
    """

    _instance = None  # Singleton

    def __new__(cls, input_name: Path | str | None = None) -> "BaseLogger":
        """Init or return the singleton logger instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_logger(input_name)
        return cls._instance

    def _init_logger(self, input_name: Path | str | None = None) -> None:
        """Initialize the internal logger, handlers and formatters.

        Args:
          input_name: Optional name used to create or locate the log
            file (defaults to 'app').
        """
        self._has_error = False
        self.base_folder = Path("logs")

        self.logger = logging.getLogger("SystemLogger")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

        file_formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s",
            datefmt="%H:%M:%S",
        )

        console_formatter = ColoredFormatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s",
            datefmt="%H:%M:%S",
        )

        # File handler
        self.log_path, file_handler = self._setup_handler(input_name)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)

        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def _setup_handler(
        self,
        input_name: Path | str | None = None,
    ) -> tuple[Path, logging.FileHandler]:
        """Create and return a file handler for application logs.

        Args:
          input_name: Optional identifier used to name the log file.

        Returns:
          A tuple containing the Path to the log file and the
          configured file handler instance.
        """
        os.makedirs(self.base_folder, exist_ok=True)
        log_path = self.base_folder / f"{(input_name or 'app')}.log"
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        return log_path, file_handler

    def info(self, msg: str) -> None:
        """Log an informational message.

        Args:
          msg: Message to log at INFO level.
        """
        self.logger.info(msg, stacklevel=2)

    def debug(self, msg: str) -> None:
        """Log a debug-level message.

        Args:
          msg: Message to log at DEBUG level.
        """
        self.logger.debug(msg, stacklevel=2)

    def warning(self, msg: str) -> None:
        """Log a warning-level message.

        Args:
          msg: Message to log at WARNING level.
        """
        self.logger.warning(msg, stacklevel=2)

    def error(self, msg: str) -> None:
        """Log an error message and mark that an error occurred.

        Args:
          msg: Message to log at ERROR level.
        """
        self._has_error = True
        self.logger.error(msg, stacklevel=2)

    def critical(self, msg: str) -> None:
        """Log a critical-level message.

        Args:
          msg: Message to log at CRITICAL level.
        """
        self.logger.critical(msg, stacklevel=2)

    def get_log_path(self) -> Path:
        """Return the current log file path.

        Returns:
          Path: Path to the active log file.
        """
        return self.log_path

    def has_errors(self) -> bool:
        """Return whether an error has been logged during runtime.

        Returns:
          bool: True if any error was logged, otherwise False.
        """
        return self._has_error


class TimeLogger(BaseLogger):
    """Logger that writes timestamped log files into a per-run folder.

    This variant of :class:`BaseLogger` creates a new timestamped file
    for each run inside ``logs/<input_name>/`` which is useful when
    keeping separate logs per execution is desired.
    """

    def _setup_handler(
        self,
        input_name: Path | str | None = None,
    ) -> tuple[Path, logging.FileHandler]:
        """Create a timestamped file handler for a single run.

        Args:
          input_name: Optional identifier used to name the folder.

        Returns:
          A tuple (log_path, file_handler) where log_path is the Path to the
          created log file and file_handler is the configured handler.
        """
        timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        log_dir = self.base_folder / (input_name or "app")
        os.makedirs(log_dir, exist_ok=True)
        log_path = log_dir / f"{timestamp}.log"

        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        return log_path, file_handler


class RotLogger(BaseLogger):
    """Logger using a rotating file handler to bound log file size.

    RotLogger uses :class:`logging.handlers.RotatingFileHandler` to
    keep logs from growing indefinitely by rotating them when they
    exceed a configured size.
    """

    def _setup_handler(
        self,
        input_name: Path | str | None = None,
    ) -> tuple[Path, logging.FileHandler]:
        """Create a rotating file handler for application logs.

        Args:
          input_name: Optional identifier for the log folder.

        Returns:
          A tuple (log_path, file_handler) of the configured rotating handler.
        """
        log_dir = self.base_folder / (input_name or "app")
        os.makedirs(log_dir, exist_ok=True)
        log_path = log_dir / f"{(input_name or 'app')}.log"

        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )

        return log_path, file_handler


logger = RotLogger("app")


def get_logger() -> RotLogger:
    """Return the module-level configured logger instance.

    Returns:
      RotLogger: The shared logger instance used by the application.
    """
    return logger
