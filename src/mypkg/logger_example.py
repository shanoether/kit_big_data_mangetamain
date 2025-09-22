from src.utils.logger import BaseLogger
from src.mypkg.logger_example_helper import run_from_another_file

def run():
    logger = BaseLogger()
    logger.info("Entering main.py")
    run_from_another_file()

if __name__ == "__main__":
    logger = BaseLogger("logger_example")
    run()
