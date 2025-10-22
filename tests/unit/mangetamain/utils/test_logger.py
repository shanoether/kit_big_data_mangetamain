import os
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler

import unittest
from unittest.mock import MagicMock, patch
import tempfile

from mangetamain.utils.logger import BaseLogger, TimeLogger, RotLogger, get_logger

class TestBaseLogger(unittest.TestCase):
    def setUp(self):
        BaseLogger._instance = None
        self.logger_name = "test_log"

    def test_singleton_behavior(self):
        logger1 = BaseLogger(self.logger_name)
        logger2 = BaseLogger(self.logger_name)
        self.assertIs(logger1, logger2, "BaseLogger should implement singleton pattern")

    def test_log_file_creation(self):
        logger = BaseLogger(self.logger_name)
        log_path = logger.get_log_path()
        self.assertTrue(log_path.exists(), "Log file should be created")
        self.assertTrue(log_path.is_file(), "Log path should point to a file")
        self.assertIn(self.logger_name, log_path.name)

    def test_info(self):
        logger = BaseLogger(self.logger_name)

        # Patch logger methods to capture calls
        with patch.object(logger.logger, 'info') as mock_info:
            logger.info("Info message")
            mock_info.assert_called_once_with("Info message", stacklevel=2)

    def test_debug(self):
        logger = BaseLogger(self.logger_name)

        # Patch logger methods to capture calls
        with patch.object(logger.logger, 'debug') as mock_debug:
            logger.debug("Debug message")
            mock_debug.assert_called_once_with("Debug message", stacklevel=2)
    
    def test_warning(self):
        logger = BaseLogger(self.logger_name)

        # Patch logger methods to capture calls
        with patch.object(logger.logger, 'warning') as mock_warning:
            logger.warning("Warning message")
            mock_warning.assert_called_once_with("Warning message", stacklevel=2)
    
    def test_error(self):
        logger = BaseLogger(self.logger_name)

        # Patch logger methods to capture calls
        with patch.object(logger.logger, 'error') as mock_error:
            logger.error("Error message")
            mock_error.assert_called_once_with("Error message", stacklevel=2)

    def test_critical(self):
        logger = BaseLogger(self.logger_name)

        # Patch logger methods to capture calls
        with patch.object(logger.logger, 'critical') as mock_critical:
            logger.critical("Critical message")
            mock_critical.assert_called_once_with("Critical message", stacklevel=2)

    def test_has_errors_flag(self):
        logger = BaseLogger(self.logger_name)
        self.assertFalse(logger.has_errors(), "Initially, has_errors should be False")
        logger.error("Test error")
        self.assertTrue(logger.has_errors(), "After logging an error, has_errors should be True")

    def tearDown(self):
        # Clean up created log files
        logger = BaseLogger(self.logger_name)
        if logger.get_log_path().exists():
            os.remove(logger.get_log_path())


class TestTimeLogger(unittest.TestCase):
    def setUp(self):
        # Reset singleton for each test
        TimeLogger._instance = None
        self.logger_name = "time_test"

    def test_singleton_behavior(self):
        logger1 = TimeLogger(self.logger_name)
        logger2 = TimeLogger(self.logger_name)
        self.assertIs(logger1, logger2, "TimeLogger should implement singleton pattern")

    def test_timestamped_log_file_creation(self):
        logger = TimeLogger(self.logger_name)
        log_path = logger.get_log_path()
        self.assertTrue(log_path.exists(), "Timestamped log file should be created")
        self.assertTrue(log_path.is_file(), "Log path should point to a file")
        self.assertTrue(log_path.name.endswith(".log"))

    def tearDown(self):
        # Clean up created files and folders
        logger = TimeLogger(self.logger_name)
        log_path = logger.get_log_path()
        if log_path.exists():
            os.remove(log_path)
        log_dir = log_path.parent
        if log_dir.exists():
            os.rmdir(log_dir)


class TestRotLogger(unittest.TestCase):
    def setUp(self):
        RotLogger._instance = None
        self.logger_name = "rot_test"

    def test_singleton_behavior(self):
        logger1 = RotLogger(self.logger_name)
        logger2 = RotLogger(self.logger_name)
        self.assertIs(logger1, logger2, "RotLogger should implement singleton pattern")

    def test_rotating_file_handler_setup(self):
        logger = RotLogger(self.logger_name)
        log_path = logger.get_log_path()
        self.assertTrue(log_path.exists(), "Rotating log file should be created")
        self.assertIsInstance(logger.logger.handlers[0], RotatingFileHandler, "Handler should be RotatingFileHandler")

    def tearDown(self):
        logger = RotLogger(self.logger_name)
        log_path = logger.get_log_path()
        if log_path.exists():
            os.remove(log_path)
        log_dir = log_path.parent
        if log_dir.exists():
            os.rmdir(log_dir)

def test_get_logger_instance():
    logger1 = get_logger()
    logger2 = get_logger()
    assert logger1 is logger2, "get_logger should return the same RotLogger instance"

if __name__ == "__main__":
    unittest.main()
