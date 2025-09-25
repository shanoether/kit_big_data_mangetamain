from src.utils.logger import RotLogger
from src.mypkg.logger_example_helper import run_from_another_file

def run():
    logger = RotLogger()
    logger.warning("Entering main.py")
    run_from_another_file()

if __name__ == "__main__":
    logger = RotLogger("logger_example")
    run()
