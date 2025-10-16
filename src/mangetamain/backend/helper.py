import streamlit as st
import polars as pl

from mangetamain.utils.logger import get_logger

logger = get_logger()

@st.cache_data
def load_csv_with_progress(file_path: str) -> tuple[pl.DataFrame, float]:
    """Load a CSV file with a progress bar.

    Args:
      file_path: Path to the CSV file.
      file_path: str:
      file_path: str: 

    Returns:
      : A tuple containing the loaded DataFrame and the time taken to load it.

    """
    import time
    start_time = time.time()
    with st.spinner(f"Loading data from {file_path}..."):
        df = pl.read_csv(file_path)
    end_time = time.time()
    load_time = end_time - start_time
    logger.info(f"Data loaded successfully from {file_path} in {load_time:.2f} seconds.")
    return df, load_time

@st.cache_data
def load_parquet_with_progress(file_path: str) -> tuple[pl.DataFrame, float]:
    """Load a Parquet file with a progress bar.

    Args:
      file_path: Path to the Parquet file.
      file_path: str:
      file_path: str: 

    Returns:
      : A tuple containing the loaded DataFrame and the time taken to load it.

    """
    with st.spinner(f"Loading data from {file_path}..."):
        df = pl.read_parquet(file_path)
    logger.info(f"Data loaded successfully from {file_path}.")
    return df