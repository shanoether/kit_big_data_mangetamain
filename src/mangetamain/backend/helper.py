"""Helper functions for data loading with progress indication in Streamlit."""

import time

import polars as pl
import streamlit as st

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
    with st.spinner(f"Loading data from {file_path}..."):
        df = pl.read_parquet(file_path)
    logger.info(f"Data loaded successfully from {file_path}.")
    return df
