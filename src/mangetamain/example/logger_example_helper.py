from mangetamain.utils.logger import RotLogger

def run_from_another_file():
    logger = RotLogger()
    logger.info("Running from logger_example_helper.py")