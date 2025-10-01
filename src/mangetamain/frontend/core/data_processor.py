import pandas as pd
import numpy as np

from mangetamain.utils import logger
from mangetamain.utils.logger import RotLogger


class DataProcessor:
    def __init__(self):
        self.data = None
        self.logger = RotLogger()
        self.logger.info("DataProcessor initialized")

    def set_data(self, data):
        self.data = data
        self.logger.info(f"Data loaded with shape: {data.shape}")
        return self

    def get_data(self):
        return self.data
    
