"""Unit tests for the RotLogger in mangetamain.utils.logger."""

from mangetamain.utils.logger import get_logger


def test_logger_basic(tmp_path: str) -> None:
    """Test that logger writes messages at all levels and creates a log file."""
    # Use a temporary log file location
    log_name = "testlog"
    logger = get_logger()
    logger._init_logger(tmp_path / log_name)

    logger.info("Info message")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    log_path = logger.get_log_path()
    assert log_path.exists(), f"Log file {log_path} should exist."
    content = log_path.read_text()
    # Check that all log levels appear in the file
    for level in ["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"]:
        assert level in content, f"Log level {level} not found in log file."
    # Check that error flag is set
    assert logger.has_errors() is True
