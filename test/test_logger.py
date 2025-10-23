import pytest
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock
from mangetamain.utils.logger import BaseLogger, RotLogger, TimeLogger, get_logger

def test_singleton_behavior():
    logger1 = BaseLogger("test")
    logger2 = BaseLogger("test")
    assert logger1 is logger2, "BaseLogger should be a singleton"

def test_log_path_creation(tmp_path):
    # Patch BaseLogger base_folder pour utiliser tmp_path
    with patch.object(BaseLogger, "base_folder", tmp_path):
        rot_logger = RotLogger("test_app")
        log_path = rot_logger.get_log_path()
        assert log_path.parent.exists()
        assert log_path.suffix == ".log"
        assert log_path.name.startswith("test_app")

def test_logging_methods(tmp_path):
    with patch.object(BaseLogger, "base_folder", tmp_path):
        rot_logger = RotLogger("test_app2")
        # Patch les handlers pour ne rien écrire sur disque
        rot_logger.logger.handlers = []
        mock_handler = MagicMock()
        rot_logger.logger.addHandler(mock_handler)
        
        # Appel des méthodes
        rot_logger.info("info msg")
        rot_logger.debug("debug msg")
        rot_logger.warning("warn msg")
        rot_logger.error("error msg")
        rot_logger.critical("crit msg")
        
        # Vérifie qu'un message a été envoyé au handler
        assert mock_handler.handle.call_count == 5
        # Vérifie que has_errors est à True après un error
        assert rot_logger.has_errors() is True

def test_time_logger_creates_timestamped_file(tmp_path):
    with patch.object(TimeLogger, "base_folder", tmp_path):
        time_logger = TimeLogger("timed_app")
        log_path = time_logger.get_log_path()
        assert log_path.name.endswith(".log")
        assert len(log_path.stem.split("_")) > 1  # timestamp inclus

def test_get_logger_returns_singleton():
    logger_a = get_logger()
    logger_b = get_logger()
    assert logger_a is logger_b
    assert isinstance(logger_a, RotLogger)
