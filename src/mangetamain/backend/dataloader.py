"""Data loading module for Mangetamain food rating application.

This module handles the extraction and loading of food rating data from
zip archives into Polars DataFrames. It provides functionality for loading
both interaction data (ratings) and recipe data.
"""

import zipfile
from pathlib import Path

import polars as pl
import streamlit as st

from mangetamain.utils.logger import RotLogger


class DataLoader:
    """Class responsible for loading the data.

    This class handles loading interaction and recipe data from specified zip files.
    It provides methods to load each dataset separately as Polars DataFrames.

    Attributes:
        logger: A rotating logger instance for tracking data loading operations
        path_interactions: Path to the zipped interactions CSV file
        path_recipes: Path to the zipped recipes CSV file
    """

    def __init__(
        self,
        path_interactions: Path = Path("data/raw/RAW_interactions.csv.zip"),
        path_recipes: Path = Path("data/raw/RAW_recipes.csv.zip"),
    ) -> None:
        """Initialize the DataLoader with paths to data files.

        Args:
            path_interactions: Path to the zipped interactions CSV file.
                Defaults to 'data/raw/RAW_interactions.csv.zip'.
            path_recipes: Path to the zipped recipes CSV file.
                Defaults to 'data/raw/RAW_recipes.csv.zip'.
        """
        self.logger = RotLogger()
        self.logger.info("Starting to load data.")
        self.path_interactions = path_interactions
        self.path_recipes = path_recipes

    @st.cache_data
    def load_interactions(self) -> pl.DataFrame:
        """Loads interaction data from a zip file and returns it as a Polars DataFrame.

        This method extracts the interactions CSV file from the zip archive and loads
        it into a Polars DataFrame. The date column is converted to Datetime type.

        Returns:
            pl.DataFrame: A Polars DataFrame containing the interactions data with the
                following columns: user_id, recipe_id, date, rating, review.

        Raises:
            zipfile.BadZipFile: If the specified zip file is invalid or corrupted.
            FileNotFoundError: If the interactions zip file doesn't exist.
        """
        with (
            zipfile.ZipFile(self.path_interactions) as zf,
            zf.open(zf.namelist()[0]) as f,
        ):  # assuming only one file inside
            df_interactions = pl.read_csv(f, schema_overrides={"date": pl.Datetime})
        self.logger.info(
            f"Interactions loaded successfully | Data shape: {df_interactions.shape}.",
        )
        return df_interactions

    @st.cache_data
    def load_recipes(self) -> pl.DataFrame:
        """Loads recipe data from a zip file and returns it as a Polars DataFrame.

        This method extracts the recipes CSV file from the zip archive and loads
        it into a Polars DataFrame. The submitted column is converted to Datetime type.

        Returns:
            pl.DataFrame: A Polars DataFrame containing the recipes data with columns
                such as recipe_id, name, minutes, contributor_id, submitted, tags,
                nutrition, n_steps, steps, description, ingredients, n_ingredients.

        Raises:
            zipfile.BadZipFile: If the specified zip file is invalid or corrupted.
            FileNotFoundError: If the recipes zip file doesn't exist.
        """
        with (
            zipfile.ZipFile(self.path_recipes) as zf,
            zf.open(zf.namelist()[0]) as f,
        ):  # assuming only one file inside
            df_recipes = pl.read_csv(f, schema_overrides={"submitted": pl.Datetime})
        self.logger.info(
            f"Recipes loaded successfully | Data shape: {df_recipes.shape}.",
        )
        return df_recipes


if __name__ == "__main__":
    """Simple test to load data when this file is run directly."""
    loader = DataLoader()
    interactions = loader.load_interactions()
    recipes = loader.load_recipes()
    print(
        f"Loaded {interactions.shape[0]} interactions and {recipes.shape[0]} recipes.",
    )