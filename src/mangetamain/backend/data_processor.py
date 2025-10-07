"""Data processing module for Mangetamain food rating application.

This module provides functionality for transforming and enriching food
rating data. It includes operations like extracting year information from
dates and preparing data for visualization.
"""

from pathlib import Path
import zipfile

import polars as pl

from mangetamain.utils.logger import get_logger

logger = get_logger()

class DataProcessor:
    """Processes and transforms recipe and interaction data."""

    def __init__(self, 
                 path_interactions: Path = Path("data/raw/RAW_interactions.csv.zip"),
                 path_recipes: Path = Path("data/raw/RAW_recipes.csv.zip")
                 ) -> None:
        """Initialize with interaction and recipe dataframes.

        Args:
            interactions: Interaction data
            recipes: Recipe data
        """
        logger.info("Starting to load data.")
        self.path_interactions = path_interactions
        self.path_recipes = path_recipes
        self.interactions, self.recipes = self.load_data_from_zip()
    
    def load_data_from_zip(self):
        """Load data from zip files into Polars DataFrames.

        Returns:
            Tuple of interactions and recipes dataframes
        """
        with (
            zipfile.ZipFile(self.path_interactions) as zf,
            zf.open(zf.namelist()[0]) as f,
        ):  # assuming only one file inside
            df_interactions = pl.read_csv(f, schema_overrides={"date": pl.Datetime})
        logger.info(
            f"Interactions loaded successfully | Data shape: {df_interactions.shape}.",
        )
        with (
            zipfile.ZipFile(self.path_recipes) as zf,
            zf.open(zf.namelist()[0]) as f,
        ):  # assuming only one file inside
            df_recipes = pl.read_csv(f, schema_overrides={"submitted": pl.Datetime})
        logger.info(
            f"Recipes loaded successfully | Data shape: {df_recipes.shape}.",
        )

        return df_interactions, df_recipes

    def add_year_column(self) -> tuple[pl.DataFrame, pl.DataFrame]:
        """Extract year from date columns for both dataframes.

        Returns:
            Tuple of updated interactions and recipes dataframes
        """
        logger.info("Adding year column to interactions and recipes dataframes.")
        self.interactions = self.interactions.with_columns(
            year=pl.col("date").dt.year(),
        )
        self.recipes = self.recipes.with_columns(year=pl.col("submitted").dt.year())
        logger.info("Year column added to interactions and recipes dataframes.")
        return self.interactions, self.recipes

    def save_data(self) -> None:
        """
        Save processed dataframes to parquet files.
        """
        save_folder = Path("data/processed")
        save_folder.mkdir(parents=True, exist_ok=True)
        self.interactions.write_parquet("data/processed/processed_interactions.parquet")
        self.recipes.write_parquet("data/processed/processed_recipes.parquet")
        logger.info("Processed data saved to parquet files.")

if __name__ == "__main__":
    processor = DataProcessor()
    processor.add_year_column()
    processor.save_data()
    logger.info("Data processing completed.")
