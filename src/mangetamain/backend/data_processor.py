"""Data processing module for Mangetamain food rating application.

This module provides functionality for transforming and enriching food
rating data. It includes operations like extracting year information from
dates and preparing data for visualization.
"""

import zipfile
import polars as pl
import numpy as np
from pathlib import Path

from mangetamain.utils.logger import get_logger

logger = get_logger()

class DataProcessor:
    """Processes and transforms recipe and interaction data."""

    def __init__(self, data_dir: Path = Path("data/raw"),
                 path_interactions: Path = Path("data/raw/RAW_interactions.csv"),
                 path_recipes: Path = Path("data/raw/RAW_recipes.csv")
                 ) -> None:
        """Initialize with interaction and recipe dataframes.

        Args:
            interactions: Interaction data
            recipes: Recipe data
        """
        logger.info("Starting to load data.")
        self.data_dir = data_dir
        self.path_interactions = path_interactions
        self.path_recipes = path_recipes
        self.df_interactions, self.df_recipes = self.load_data()
    
    def load_data(self):
        """Load data from csv or zip files into Polars DataFrames.

        Args:
            path_interactions: Path to the interactions zip file
            path_recipes: Path to the recipes zip file
        """
        
        # Check if CSV files exist, otherwise look for ZIP files
        if not self.path_interactions.exists() or not self.path_recipes.exists():
            logger.info("CSV files not found, checking for ZIP files.")
            path_interaction_zip = self.path_interactions.with_suffix('.csv.zip')
            path_recipes_zip = self.path_recipes.with_suffix('.csv.zip')

            if not path_interaction_zip.exists() or not path_recipes_zip.exists():
                logger.error(f"CSV and ZIP files not found: {path_interaction_zip} and {path_recipes_zip} not found.")
                raise FileNotFoundError("Neither CSV nor ZIP files found for interactions or recipes.")
            else:
                logger.info("Extracting data from ZIP files.")
                with zipfile.ZipFile(path_interaction_zip, 'r') as zip_ref:
                    zip_ref.extractall(self.data_dir)
                with zipfile.ZipFile(path_recipes_zip, 'r') as zip_ref:
                    zip_ref.extractall(self.data_dir)
                    
        # Load data from CSV
        
        try:
            with open(self.path_interactions, 'rb') as f:
                df_interactions = pl.read_csv(f, schema_overrides={"date": pl.Datetime})
                logger.info(f"Interactions loaded successfully | Data shape: {df_interactions.shape}.")
            with open(self.path_recipes, 'rb') as f:
                df_recipes = pl.read_csv(f, schema_overrides={"submitted": pl.Datetime})
                df_recipes = df_recipes.rename({"id": "recipe_id"})
                logger.info(f"Recipes loaded successfully | Data shape: {df_recipes.shape}.")
        except Exception as e:
            logger.error(f"Error loading CSV files: {e}")
            raise   
        
        return df_interactions, df_recipes
    
    
    def drop_na(self) -> None:
        self.df_interactions = self.df_interactions.filter(~self.df_interactions["review"].is_null())
        logger.info(f"Interactions after dropping NA | Data shape: {self.df_interactions.shape}.")
        self.df_recipes_nna = self.df_recipes.filter((self.df_recipes["minutes"] < 60*24*365) & (self.df_recipes["minutes"] == 0))
        logger.info(f"Recipes after dropping unrealistic times | Data shape: {self.df_recipes.shape}.")
        self.df_recipes_nna = self.df_recipes.filter(self.df_recipes["n_steps"] > 0)
        logger.info(f"Recipes after dropping zero steps | Data shape: {self.df_recipes.shape}.")

    def split_minutes(self) -> None:
        """Split recipes into short, medium, and long based on preparation time."""
        self.df_recipes_nna_short = self.df_recipes_nna.filter(self.df_recipes_nna["minutes"] <= 100)
        self.df_recipes_nna_medium = self.df_recipes_nna.filter((self.df_recipes_nna["minutes"] > 100) & (self.df_recipes_nna["minutes"] <= 60 * 48))
        self.df_recipes_nna_long = self.df_recipes_nna.filter(self.df_recipes_nna["minutes"] > 60 * 48)
        logger.info(
            f"Recipes split into short ({self.df_recipes_nna_short.shape}), "
            f"medium ({self.df_recipes_nna_medium.shape}), "
            f"and long ({self.df_recipes_nna_long.shape}).",
        )
    
    def merge_data(self) -> None:
        """Merge interactions with recipes on recipe_id."""
        self.total = self.df_interactions.join(
            self.df_recipes_nna, left_on="recipe_id", right_on="recipe_id", how="inner"
        )
        self.total_short = self.df_interactions.join(
            self.df_recipes_nna_short, left_on="recipe_id", right_on="recipe_id", how="inner"
        )
        self.total_medium = self.df_interactions.join(
            self.df_recipes_nna_medium, left_on="recipe_id", right_on="recipe_id", how="inner"
        )
        self.total_long = self.df_interactions.join(
            self.df_recipes_nna_long, left_on="recipe_id", right_on="recipe_id", how="inner"
        )
        logger.info(f"Merged data shape: {self.total.shape}.")
        logger.info(f"Merged short recipes data shape: {self.total_short.shape}.")
        logger.info(f"Merged medium recipes data shape: {self.total_medium.shape}.")
        logger.info(f"Merged long recipes data shape: {self.total_long.shape}.")

    def compute_proportions(self) -> None:
        #minutes = np.array(sorted(self.df_recipes_nna_court["minutes"].unique()))
        minutes = np.array(sorted(self.df_recipes_nna_short["minutes"].unique()))
        proportion_m = [0 for m in minutes]
        for m in range(len(minutes)):
            #comptes = self.df_total_court.filter(pl.col("minutes") == minutes[m])["rating"].value_counts().sort("rating")
            comptes = self.total_short.filter(pl.col("minutes") == minutes[m])["rating"].value_counts().sort("rating")
            proportion_m[m] = (comptes.filter(pl.col("rating") == 5) / comptes.sum())[0,1]
        #proportion_m = pl.Series(np.array(proportion_m))
        proportion_m = np.array(proportion_m)

        #steps = np.array(sorted(self.df_recipes_nna[self.df_recipes_nna["n_steps"] <= 40].n_steps.unique()))
        steps = np.array(sorted(self.df_recipes_nna.filter(pl.col("n_steps") <= 40).select(pl.col("n_steps")).unique().to_series().to_list()))
        proportion_s = [0 for m in steps]
        for m in range(len(steps)):
            comptes = self.total.filter(pl.col("n_steps") == steps[m])["rating"].value_counts().sort("rating")
            #proportion_s[m] = (comptes[5] / comptes.sum())[0,1]
            proportion_s[m] = (comptes.filter(pl.col("rating") == 5) / comptes.sum())[0,1] # Sometimes missing ratings so fetching index 5 is out of bound
        #proportion_s = pl.Series(np.array(proportion_s))
        proportion_s = np.array(proportion_s)


        self.df_proportion_m = pl.DataFrame({"minutes": minutes.astype(int), "proportion_m": proportion_m.astype(float)}) # type conversion needed for parquet
        self.df_proportion_s = pl.DataFrame({"n_steps": steps.astype(int), "proportion_s": proportion_s.astype(float)})


    def save_data(self) -> None:
        """
        Save processed dataframes to parquet files.
        """
        save_folder = Path("data/processed")
        save_folder.mkdir(parents=True, exist_ok=True)
        self.df_interactions.write_parquet("data/processed/processed_interactions.parquet")
        self.df_recipes.write_parquet("data/processed/processed_recipes.parquet")
        self.total.write_parquet("data/processed/total.parquet")
        self.total_short.write_parquet("data/processed/short.parquet")
        #self.df_recipes_nna_medium.write_parquet("data/processed/medium.parquet")
        #self.df_recipes_nna_long.write_parquet("data/processed/long.parquet")
        self.df_proportion_m.write_parquet("data/processed/proportion_m.parquet")
        self.df_proportion_s.write_parquet("data/processed/proportion_s.parquet")
        logger.info("Processed data saved to parquet files.")

if __name__ == "__main__":
    processor = DataProcessor()
    processor.drop_na()
    processor.split_minutes()
    processor.merge_data()
    processor.compute_proportions()
    processor.save_data()
    logger.info("Data processing completed.")
