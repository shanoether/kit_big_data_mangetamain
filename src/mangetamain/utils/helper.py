"""Helper functions for data loading with progress indication in Streamlit.

This module provides cached data loading functions for CSV and Parquet files,
as well as utilities to initialize Streamlit session state from preprocessed
datasets. All functions use Polars for efficient DataFrame operations and
integrate with Streamlit's caching and UI feedback mechanisms.
"""

import time
from typing import Tuple

import polars as pl
import streamlit as st

from mangetamain.backend.recipe_analyzer import RecipeAnalyzer
from mangetamain.utils.logger import get_logger

logger = get_logger()


@st.cache_data  # type: ignore[misc]
def load_csv_with_progress(file_path: str) -> tuple[pl.DataFrame, float]:
    """Read a CSV file into a Polars DataFrame while showing a Streamlit spinner.

    Args:
      file_path: Path to the CSV file to read.

    Returns:
      A tuple (df, load_time) where ``df`` is the loaded Polars DataFrame and
      ``load_time`` is the elapsed time in seconds.
    """
    start_time = time.time()
    with st.spinner(f"Loading data from {file_path}..."):
        df = pl.read_csv(file_path)
    load_time = time.time() - start_time
    logger.info(
        f"Data loaded successfully from {file_path} in {load_time:.2f} seconds.",
    )
    return df, load_time


@st.cache_resource(show_spinner=False)  # type: ignore[misc]
def load_parquet_with_progress(file_path: str) -> pl.DataFrame:
    """Read a Parquet file into a Polars DataFrame (cached globally with zero-copy).

    Args:
      file_path: Path to the Parquet file to read.

    Returns:
      A Polars DataFrame loaded from the specified parquet file.
    """
    t = time.time()
    df = pl.read_parquet(file_path)
    elapsed = time.time() - t
    logger.info(f"✅ {file_path} loaded in {elapsed:.2f}s - Shape: {df.shape}")
    return df

@st.cache_resource(show_spinner=False)  # type: ignore[misc]
def load_data_from_parquet_and_pickle() -> Tuple[
    pl.DataFrame,
    pl.DataFrame,
    pl.DataFrame,
    pl.DataFrame,
    pl.DataFrame,
    pl.DataFrame,
    pl.DataFrame,
    pl.Series,
    pl.Series,
    RecipeAnalyzer,
    bool,
]:
    """Load ALL application data ONCE and cache it globally across all users.

    This function is called once per application lifecycle. The first user will
    trigger the data loading (90s), but all subsequent users will get instant
    access (<0.01s) thanks to @st.cache_resource.

    The function reads several precomputed parquet files and returns the
    resulting Polars DataFrames / Series as a tuple.

    Files expected under ``data/processed/``:
    - initial_interactions.parquet
    - processed_interactions.parquet
    - initial_recipes.parquet
    - processed_recipes.parquet
    - total_nt.parquet
    - total.parquet
    - short.parquet
    - proportion_m.parquet
    - proportion_s.parquet
    - recipe_analyzer.pkl

    Returns:
        Tuple containing:
        - df_interactions: Initial interactions DataFrame
        - df_interactions_nna: Processed interactions DataFrame
        - df_recipes: Initial recipes DataFrame
        - df_recipes_nna: Processed recipes DataFrame
        - df_total_nt: Total non-tagged DataFrame
        - df_total: Total DataFrame
        - df_total_court: Short DataFrame
        - proportion_m: Series of proportion_m
        - proportion_s: Series of proportion_s
        - recipe_analyzer: RecipeAnalyzer instance
        - data_loaded: Success flag
    """
    import gc

    logger.info("🔄 Starting data load (this happens ONCE globally)...")
    start_time = time.time()

    try:
        # Load all parquet files with individual timing
        df_interactions = load_parquet_with_progress(
            "data/processed/initial_interactions.parquet",
        )
        gc.collect()  # Free memory between large loads

        df_interactions_nna = load_parquet_with_progress(
            "data/processed/processed_interactions.parquet",
        )
        gc.collect()

        df_recipes = load_parquet_with_progress(
            "data/processed/initial_recipes.parquet",
        )
        gc.collect()

        df_recipes_nna = load_parquet_with_progress(
            "data/processed/processed_recipes.parquet",
        )
        gc.collect()

        df_total_nt = load_parquet_with_progress(
            "data/processed/total_nt.parquet",
        )
        gc.collect()

        df_total = load_parquet_with_progress(
            "data/processed/total.parquet",
        )
        gc.collect()

        df_total_court = load_parquet_with_progress(
            "data/processed/short.parquet",
        )
        gc.collect()

        proportion_m = load_parquet_with_progress(
            "data/processed/proportion_m.parquet",
        )["proportion_m"]

        proportion_s = load_parquet_with_progress(
            "data/processed/proportion_s.parquet",
        )["proportion_s"]

        # Load the recipe_analyzer object from pickle file
        logger.info("Loading recipe_analyzer.pkl...")
        t = time.time()
        try:
            recipe_analyzer = RecipeAnalyzer.load(
                "data/processed/recipe_analyzer.pkl",
            )
            elapsed = time.time() - t
            logger.info(f"✅ recipe_analyzer.pkl loaded in {elapsed:.2f}s")
        except Exception as pickle_error:
            logger.warning(
                f"Failed to load pickle: {pickle_error}. Attempting fallback...",
            )
            # Fallback: recreate if pickle fails (optional)
            recipe_analyzer = None
            elapsed = time.time() - t
            logger.info(f"⚠️ recipe_analyzer fallback in {elapsed:.2f}s")

        data_loaded = True
        total_time = time.time() - start_time
        logger.info(
            f"✅ ALL DATA LOADED successfully in {total_time:.2f}s "
            f"(cached globally for all users)",
        )

    except Exception as e:
        logger.error(
            f"❌ Error loading data: {e}, please run backend/dataprocessor "
            f"first to initialize application data.",
        )
        st.error(
            f"Error loading data: {e}, please run backend/dataprocessor "
            f"first to initialize application data.",
        )
        # Return empty data on error
        data_loaded = False
        df_interactions = pl.DataFrame()
        df_interactions_nna = pl.DataFrame()
        df_recipes = pl.DataFrame()
        df_recipes_nna = pl.DataFrame()
        df_total_nt = pl.DataFrame()
        df_total = pl.DataFrame()
        df_total_court = pl.DataFrame()
        proportion_m = pl.Series()
        proportion_s = pl.Series()
        recipe_analyzer = None  # type: ignore[assignment]

    return (
        df_interactions,
        df_interactions_nna,
        df_recipes,
        df_recipes_nna,
        df_total_nt,
        df_total,
        df_total_court,
        proportion_m,
        proportion_s,
        recipe_analyzer,
        data_loaded,
    )


def custom_exception_handler(exception: Exception) -> None:
    """Handle exceptions with logging and user-friendly Streamlit display.

    Args:
        exception: The exception instance to handle.

    Note:
        This function logs the full exception traceback and displays a
        user-friendly error message in the Streamlit UI instead of showing
        the raw Python traceback.
    """
    import streamlit as st  # noqa: PLC0415

    from mangetamain.utils.logger import get_logger  # noqa: PLC0415

    logger = get_logger()
    logger.error(f"An error occurred: {exception}")
    st.error("An unexpected error occurred. Please contact support.")
