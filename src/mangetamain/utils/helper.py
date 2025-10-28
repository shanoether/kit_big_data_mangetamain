"""Helper functions for data loading with progress indication in Streamlit.

This module provides cached data loading functions for CSV and Parquet files,
as well as utilities to initialize Streamlit session state from preprocessed
datasets. All functions use Polars for efficient DataFrame operations and
integrate with Streamlit's caching and UI feedback mechanisms.
"""

import time

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


@st.cache_data  # type: ignore[misc]
def load_parquet_with_progress(file_path: str) -> pl.DataFrame:
    """Read a Parquet file into a Polars DataFrame while showing a Streamlit spinner.

    Args:
      file_path: Path to the Parquet file to read.

    Returns:
      A Polars DataFrame loaded from the specified parquet file.
    """
    df = pl.read_parquet(file_path)
    logger.info(f"Data loaded successfully from {file_path}.")
    return df


def load_data_from_parquet_and_pickle() -> bool:
    """Load application data from parquet files into Streamlit session state.

    The function reads several precomputed parquet files and stores the
    resulting Polars DataFrames / Series into ``st.session_state`` so that
    the UI pages can access them without reloading from disk repeatedly.

    Files expected under ``data/processed/``:
    - processed_interactions.parquet
    - processed_recipes.parquet
    - total.parquet
    - short.parquet
    - proportion_m.parquet
    - proportion_s.parquet

    This is deliberately small and fails early if files are missing.
    """
    try:
        st.session_state.df_interactions = load_parquet_with_progress(
            "data/processed/initial_interactions.parquet",
        )
        st.session_state.df_interactions_nna = load_parquet_with_progress(
            "data/processed/processed_interactions.parquet",
        )
        st.session_state.df_recipes = load_parquet_with_progress(
            "data/processed/initial_recipes.parquet",
        )
        st.session_state.df_recipes_nna = load_parquet_with_progress(
            "data/processed/processed_recipes.parquet",
        )
        st.session_state.df_total_nt = load_parquet_with_progress(
            "data/processed/total_nt.parquet",
        )
        st.session_state.df_total = load_parquet_with_progress(
            "data/processed/total.parquet",
        )
        st.session_state.df_total_court = load_parquet_with_progress(
            "data/processed/short.parquet",
        )
        st.session_state.proportion_m = load_parquet_with_progress(
            "data/processed/proportion_m.parquet",
        )["proportion_m"]
        st.session_state.proportion_s = load_parquet_with_progress(
            "data/processed/proportion_s.parquet",
        )["proportion_s"]

        # Import the recipe_analyzer object from pickle file
        st.session_state.recipe_analyzer = RecipeAnalyzer.load(
            "data/processed/recipe_analyzer.pkl",
        )
        data_loaded = True

        logger.info("Data loaded into session state.")

    except Exception as e:
        logger.error(
            f"Error loading data: {e}, please run backend/dataprocessor first to initialize application data.",
        )
        st.error(
            f"Error loading data: {e}, please run backend/dataprocessor first to initialize application data.",
        )
        data_loaded = False

    st.session_state.data_loaded = data_loaded
    return data_loaded


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
