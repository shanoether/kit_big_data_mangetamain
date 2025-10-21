# test_math_functions.py

import unittest
from mangetamain.utils.logger import BaseLogger, get_logger

class TestBaseLogger(unittest.TestCase):
    def setUp(self):
        self.logger = BaseLogger("test")
    
    def test_info(self):
        logger = get_logger()
        debug_message = "This is a debug message"
        
        logger.debug(debug_message)
        
        log_content = logger.get_log_path().read_text()
        assert "DEBUG" in log_content
        assert debug_message in log_content
    
    def test_debug(self):
        logger = get_logger()
        info_message = "This is an info message"
        
        logger.info(info_message)
        
        log_content = logger.get_log_path().read_text()
        assert "INFO" in log_content
        assert info_message in log_content

    def test_debug(self):
        logger = get_logger()
        debug_message = "This is a debug message"

        logger.debug(debug_message)

        log_content = logger.get_log_path().read_text()
        assert "DEBUG" in log_content
        assert debug_message in log_content

    def test_warning(self):
        logger = get_logger()
        warning_message = "This is a warning message"

        logger.warning(warning_message)

        log_content = logger.get_log_path().read_text()
        assert "WARNING" in log_content
        assert warning_message in log_content
    
    def test_error(self):
        logger = get_logger()
        error_message = "This is an error message"

        logger.error(error_message)

        log_content = logger.get_log_path().read_text()
        assert "ERROR" in log_content
        assert error_message in log_content
        assert logger.has_errors() is True
    
    def test_critical(self):
        logger = get_logger()
        critical_message = "This is a critical message"

        logger.critical(critical_message)

        log_content = logger.get_log_path().read_text()
        assert "CRITICAL" in log_content
        assert critical_message in log_content

if __name__ == '__main__':
    unittest.main()