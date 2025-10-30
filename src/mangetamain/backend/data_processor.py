"""Data processing module for the Mangetamain project.

This module contains the :class:`DataProcessor` class which is responsible
for loading raw CSV/ZIP datasets, cleaning and splitting recipe data,
merging interactions with recipe metadata and computing simple
aggregations used by the frontend (proportions, aggregates and parquet
exports).

The class uses Polars for efficient DataFrame operations and writes the
processed results into ``data/processed/`` as parquet files.
"""

import zipfile
from pathlib import Path

import numpy as np
import polars as pl

from mangetamain.backend.recipe_analyzer import RecipeAnalyzer
from mangetamain.utils.logger import get_logger

logger = get_logger()

RATING_MAX = 5
NB_STEPS_MAX = 40
MEDIUM_LIM = 100
LONG_LIM = 60 * 48


class DataProcessor:
    """Processes and transforms recipe and interaction data.

    The :class:`DataProcessor` is a lightweight ETL helper used to build
    the processed datasets consumed by the Streamlit frontend. It exposes
    a small sequence of methods that can be called by a runner or CI job:

    - ``load_data``: Load CSV or extract ZIP and read inputs with Polars.
    - ``drop_na``: Remove rows with missing or unrealistic values.
    - ``split_minutes``: Partition recipes into short/medium/long buckets.
    - ``merge_data``: Join interactions with recipe metadata.
    - ``compute_proportions``: Compute simple aggregates used by plots.
    - ``save_data``: Persist the processed tables to parquet files.
    """

    def __init__(
        self,
        data_dir: Path = Path("data/raw"),
        path_interactions: Path = Path("data/raw/RAW_interactions.csv"),
        path_recipes: Path = Path("data/raw/RAW_recipes.csv"),
    ) -> None:
        """Initialize the DataProcessor.

        Args:
            data_dir: Base directory where raw data files live (default ``data/raw``).
            path_interactions: Path to the interactions CSV file.
            path_recipes: Path to the recipes CSV file.
        """
        logger.info("Starting to load data.")
        self.data_dir = data_dir
        self.path_interactions = path_interactions
        self.path_recipes = path_recipes
        self.df_interactions, self.df_recipes = self.load_data()

    def load_data(self) -> tuple[pl.DataFrame, pl.DataFrame]:
        """Load interactions and recipes data.

        The method accepts either CSV files or ZIP archives containing the
        CSVs. If CSV files are not present it will look for ``.csv.zip``
        siblings and extract them into ``data_dir``.

        Returns:
                A tuple ``(df_interactions, df_recipes)`` of Polars DataFrames.
        """
        # Check if CSV files exist, otherwise look for ZIP files
        if not self.path_interactions.exists() or not self.path_recipes.exists():
            logger.info("CSV files not found, checking for ZIP files.")
            path_interaction_zip = self.path_interactions.with_suffix(".csv.zip")
            path_recipes_zip = self.path_recipes.with_suffix(".csv.zip")

            if not path_interaction_zip.exists() or not path_recipes_zip.exists():
                logger.error(
                    f"CSV and ZIP files not found: {path_interaction_zip} and {path_recipes_zip} not found.",
                )
                raise FileNotFoundError(
                    "Neither CSV nor ZIP files found for interactions or recipes.",
                )
            else:
                logger.info("Extracting data from ZIP files.")
                with zipfile.ZipFile(path_interaction_zip, "r") as zip_ref:
                    zip_ref.extractall(self.data_dir)
                with zipfile.ZipFile(path_recipes_zip, "r") as zip_ref:
                    zip_ref.extractall(self.data_dir)

        # Load data from CSV

        try:
            with open(self.path_interactions, "rb") as f:
                df_interactions = pl.read_csv(f, schema_overrides={"date": pl.Datetime})
                logger.info(
                    f"Interactions loaded successfully | Data shape: {df_interactions.shape}.",
                )
            with open(self.path_recipes, "rb") as f:
                df_recipes = pl.read_csv(f, schema_overrides={"submitted": pl.Datetime})
                df_recipes = df_recipes.rename({"id": "recipe_id"})
                logger.info(
                    f"Recipes loaded successfully | Data shape: {df_recipes.shape}.",
                )
        except Exception as e:
            logger.error(f"Error loading CSV files: {e}")
            raise

        return df_interactions, df_recipes

    def drop_na(self) -> None:
        """Drop missing or unrealistic records.

        This method filters out interactions without textual reviews and
        recipes with unrealistic preparation times or zero steps. It
        updates the instance attributes used by downstream processing.
        """
        self.df_interactions_nna = self.df_interactions.filter(
            ~self.df_interactions["review"].is_null(),
        )
        logger.info(
            f"Interactions after dropping NA | Data shape: {self.df_interactions.shape}.",
        )
        self.df_recipes_nna = self.df_recipes.filter(
            (self.df_recipes["minutes"] < 60 * 24 * 365)
            & (self.df_recipes["minutes"] > 0),
        )
        logger.info(
            f"Recipes after dropping unrealistic times | Data shape: {self.df_recipes.shape}.",
        )
        self.df_recipes_nna = self.df_recipes_nna.filter(
            self.df_recipes_nna["n_steps"] > 0,
        )
        logger.info(
            f"Recipes after dropping zero steps | Data shape: {self.df_recipes.shape}.",
        )

    def split_minutes(self) -> None:
        """Split recipes into short, medium, and long buckets based on minutes.

        The thresholds are conservative and chosen to separate quick
        recipes from long projects. Results are stored on the instance as
        ``df_recipes_nna_short``, ``df_recipes_nna_medium`` and
        ``df_recipes_nna_long``.
        """
        self.df_recipes_nna_short = self.df_recipes_nna.filter(
            self.df_recipes_nna["minutes"] <= MEDIUM_LIM,
        )
        self.df_recipes_nna_medium = self.df_recipes_nna.filter(
            (self.df_recipes_nna["minutes"] > MEDIUM_LIM)
            & (self.df_recipes_nna["minutes"] <= LONG_LIM),
        )
        self.df_recipes_nna_long = self.df_recipes_nna.filter(
            self.df_recipes_nna["minutes"] > LONG_LIM,
        )
        logger.info(
            f"Recipes split into short ({self.df_recipes_nna_short.shape}), "
            f"medium ({self.df_recipes_nna_medium.shape}), "
            f"and long ({self.df_recipes_nna_long.shape}).",
        )

    def merge_data(self) -> None:
        """Join interactions with recipes on ``recipe_id``.

        Produces ``total`` tables for each duration bucket that are used to
        compute rating proportions and other aggregates.
        """
        self.total_nt = self.df_interactions.join(
            self.df_recipes,
            on="recipe_id",
            how="inner",
        )
        self.total = self.df_interactions_nna.join(
            self.df_recipes_nna,
            on="recipe_id",
            how="inner",
        )
        self.total_short = self.df_interactions_nna.join(
            self.df_recipes_nna_short,
            on="recipe_id",
            how="inner",
        )
        self.total_medium = self.df_interactions_nna.join(
            self.df_recipes_nna_medium,
            on="recipe_id",
            how="inner",
        )
        self.total_long = self.df_interactions_nna.join(
            self.df_recipes_nna_long,
            on="recipe_id",
            how="inner",
        )
        logger.info(f"Merged data shape: {self.total.shape}.")
        logger.info(f"Merged short recipes data shape: {self.total_short.shape}.")
        logger.info(f"Merged medium recipes data shape: {self.total_medium.shape}.")
        logger.info(f"Merged long recipes data shape: {self.total_long.shape}.")

    def compute_proportions(self) -> None:
        """Compute 5-star proportions by preparation time and number of steps.

        This method fills ``df_proportion_m`` and ``df_proportion_s`` which
        contain the proportion of 5-star ratings aggregated by minute and
        number-of-steps respectively. Results are suitable for plotting in
        the frontend.
        """
        # minutes = np.array(sorted(self.df_recipes_nna_court["minutes"].unique()))
        logger.info("Computing proportions of 5-star ratings by minutes")
        minutes = np.array(sorted(self.df_recipes_nna_short["minutes"].unique()))
        comptes = (
            self.total_short["minutes"]
            .value_counts()
            .sort("minutes")["count"]
            .to_numpy()
        )
        proportions = (
            self.total_short.filter(pl.col("rating") == RATING_MAX)["minutes"]
            .value_counts()
            .sort("minutes")["count"]
            .to_numpy()
        )
        proportion_m = proportions / comptes

        # steps = np.array(sorted(self.df_recipes_nna[self.df_recipes_nna["n_steps"] <= 40].n_steps.unique()))
        logger.info("Computing proportions of 5-star ratings by steps")
        steps = np.array(
            sorted(
                self.df_recipes_nna.filter(pl.col("n_steps") <= NB_STEPS_MAX)[
                    "n_steps"
                ].unique(),
            ),
        )
        comptes = (
            self.total.filter(pl.col("n_steps") <= NB_STEPS_MAX)["n_steps"]
            .value_counts()
            .sort("n_steps")["count"]
            .to_numpy()
        )
        proportions = (
            self.total.filter(
                (pl.col("n_steps") <= NB_STEPS_MAX) & (pl.col("rating") == RATING_MAX),
            )["n_steps"]
            .value_counts()
            .sort("n_steps")["count"]
            .to_numpy()
        )
        proportion_s = proportions / comptes

        logger.info("Proportions computed. Loading internally")
        self.df_proportion_m = pl.DataFrame(
            {
                "minutes": minutes.astype(int),
                "proportion_m": proportion_m.astype(float),
            },
        )  # type conversion needed for parquet
        self.df_proportion_s = pl.DataFrame(
            {"n_steps": steps.astype(int), "proportion_s": proportion_s.astype(float)},
        )

    def process_recipes(self) -> None:
        """Create a RecipeAnalyzer instance for NLP and visualization.

        Initializes a :class:`RecipeAnalyzer` with the loaded data and stores
        it as ``self.recipe_analyzer``. This object provides word cloud generation,
        TF-IDF analysis, and other recipe text analysis features.
        """
        self.recipe_analyzer = RecipeAnalyzer(
            self.df_interactions,
            self.df_recipes,
            self.total,
        )

    def user_df(self) -> None:
        """Compute user-level aggregates and store as df_user."""
        self.df_user = self.total.group_by("user_id").agg(
            nb_reviews=pl.len(),
            mean_rating=pl.col("rating").mean(),
            std_rating=pl.col("rating").std(),
            review_length=pl.col("review").flatten().str.split(" ").list.len().mean(),
            mean_time=pl.col("minutes").mean(),
        )

        self.df_user = self.df_user.with_columns(
            pl.col("std_rating").fill_nan(0).fill_null(0).alias("std_rating")
        )

    def save_data(self) -> None:
        """Persist processed tables to parquet files under ``data/processed/``.

        The output files are:
        - ``processed_interactions.parquet``
        - ``processed_recipes.parquet``
        - ``total.parquet`` (merged interactions)
        - ``short.parquet`` (merged short recipes)
        - ``proportion_m.parquet`` and ``proportion_s.parquet``
        """
        logger.info("Starting to save the data in parquet")
        save_folder = Path("data/processed")
        save_folder.mkdir(parents=True, exist_ok=True)
        logger.info("Saving df_interactions")
        self.df_interactions.write_parquet(
            "data/processed/initial_interactions.parquet",
        )
        self.df_interactions_nna.write_parquet(
            "data/processed/processed_interactions.parquet",
        )
        logger.info("Done \n Saving df_recipes")
        self.df_recipes.write_parquet("data/processed/initial_recipes.parquet")
        self.df_recipes_nna.write_parquet("data/processed/processed_recipes.parquet")

        logger.info("Done \n Saving total data")
        self.total_nt.write_parquet("data/processed/total_nt.parquet")
        self.total.write_parquet("data/processed/total.parquet")

        logger.info("Done \n Saving total short data")
        self.total_short.write_parquet("data/processed/short.parquet")
        # self.df_recipes_nna_medium.write_parquet("data/processed/medium.parquet")
        # self.df_recipes_nna_long.write_parquet("data/processed/long.parquet")

        logger.info("Done \n Saving proportions data")
        self.df_proportion_m.write_parquet("data/processed/proportion_m.parquet")
        self.df_proportion_s.write_parquet("data/processed/proportion_s.parquet")

        logger.info("Done \n Saving recipe analyzer object")

        self.recipe_analyzer.save("data/processed/recipe_analyzer.pkl")

        logger.info("Done \n Saving user data")

        self.df_user.write_parquet("data/processed/user.parquet")

        logger.info("All processed data saved to parquet files.")


if __name__ == "__main__":
    processor = DataProcessor()
    processor.drop_na()
    processor.split_minutes()
    processor.merge_data()
    processor.compute_proportions()
    processor.process_recipes()
    processor.user_df()
    processor.save_data()
    logger.info("Data processing completed.")
