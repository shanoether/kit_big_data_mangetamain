"""Data processing module for Mangetamain food rating application.

This module provides functionality for transforming and enriching food
rating data. It includes operations like extracting year information from
dates and preparing data for visualization.
"""

import polars as pl
from mangetamain.utils.logger import RotLogger


class DataProcessor:
    """Processes and transforms recipe and interaction data."""

    def __init__(self, interactions: pl.DataFrame, recipes: pl.DataFrame) -> None:
        """Initialize with interaction and recipe dataframes.

        Args:
            interactions: Interaction data
            recipes: Recipe data
        """
        self.interactions = interactions
        self.recipes = recipes
        self.logger = RotLogger()

    def add_year_column(self) -> tuple[pl.DataFrame, pl.DataFrame]:
        """Extract year from date columns for both dataframes.

        Returns:
            Tuple of updated interactions and recipes dataframes
        """
        self.logger.info("Adding year column to interactions and recipes dataframes.")
        self.interactions = self.interactions.with_columns(
            year=pl.col("date").dt.year(),
        )
        self.recipes = self.recipes.with_columns(year=pl.col("submitted").dt.year())
        self.logger.info("Year column added to interactions and recipes dataframes.")
        return self.interactions, self.recipes
