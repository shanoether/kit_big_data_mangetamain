from src.utils.logger import BaseLogger

def run_from_another_file():
    logger = BaseLogger()
    logger.info("Running from logger_example_helper.py")