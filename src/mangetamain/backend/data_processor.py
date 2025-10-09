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
        self.load_data_from_zip(path_interactions, path_recipes)
    
    def load_data_from_zip(self, path_interactions: Path, path_recipes: Path) -> None:
        """Load data from zip files into Polars DataFrames.

        Args:
            path_interactions: Path to the interactions zip file
            path_recipes: Path to the recipes zip file
        """
        with (
            zipfile.ZipFile(path_interactions) as zf,
            zf.open(zf.namelist()[0]) as f,
        ):  # assuming only one file inside
            self.df_interactions = pl.read_csv(f, schema_overrides={"date": pl.Datetime})
        logger.info(
            f"Interactions loaded successfully | Data shape: {self.df_interactions.shape}.",
        )
        with (
            zipfile.ZipFile(path_recipes) as zf,
            zf.open(zf.namelist()[0]) as f,
        ):  # assuming only one file inside
            self.df_recipes = pl.read_csv(f, schema_overrides={"submitted": pl.Datetime})
        logger.info(
            f"Recipes loaded successfully | Data shape: {self.df_recipes.shape}.",
        )

    def drop_na(self) -> None:
        self.df_interactions = self.df_interactions.filter(~self.df_interactions["review"].is_null())
        logger.info(f"Interactions after dropping NA | Data shape: {self.df_interactions.shape}.")
        self.df_recipes = self.df_recipes.filter((self.df_recipes["minutes"] < 60*24*365) & (self.df_recipes["minutes"] == 0))
        logger.info(f"Recipes after dropping unrealistic times | Data shape: {self.df_recipes.shape}.")
        self.df_recipes = self.df_recipes.filter(self.df_recipes["n_steps"] > 0)
        logger.info(f"Recipes after dropping zero steps | Data shape: {self.df_recipes.shape}.")

    def split_minutes(self) -> None:
        """Split recipes into short, medium, and long based on preparation time."""
        self.df_recipes_short = self.df_recipes.filter(self.df_recipes["minutes"] <= 100)
        self.df_recipes_medium = self.df_recipes.filter((self.df_recipes["minutes"] > 100) & (self.df_recipes["minutes"] <= 60 * 48))
        self.df_recipes_long = self.df_recipes.filter(self.df_recipes["minutes"] > 60 * 48)
        logger.info(
            f"Recipes split into short ({self.df_recipes_short.shape}), "
            f"medium ({self.df_recipes_medium.shape}), "
            f"and long ({self.df_recipes_long.shape}).",
        )
    
    def merge_data(self) -> None:
        """Merge interactions with recipes on recipe_id."""
        self.df_recipes = self.df_recipes.rename({"id": "recipe_id"})
        self.total = self.df_interactions.join(
            self.df_recipes, left_on="recipe_id", right_on="recipe_id", how="inner"
        )
        self.total_short = self.df_interactions.join(
            self.df_recipes_short, left_on="recipe_id", right_on="recipe_id", how="inner"
        )
        self.total_medium = self.df_interactions.join(
            self.df_recipes_medium, left_on="recipe_id", right_on="recipe_id", how="inner"
        )
        self.total_long = self.df_interactions.join(
            self.df_recipes_long, left_on="recipe_id", right_on="recipe_id", how="inner"
        )
        logger.info(f"Merged data shape: {self.total.shape}.")
        logger.info(f"Merged short recipes data shape: {self.total_short.shape}.")
        logger.info(f"Merged medium recipes data shape: {self.total_medium.shape}.")
        logger.info(f"Merged long recipes data shape: {self.total_long.shape}.")

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
    processor.drop_na()
    processor.split_minutes()
    processor.merge_data()
    processor.save_data()
    logger.info("Data processing completed.")
