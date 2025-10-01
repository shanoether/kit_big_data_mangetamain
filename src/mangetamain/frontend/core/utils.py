from pathlib import Path
import time

import pandas as pd
import streamlit as st

from mangetamain.utils.logger import RotLogger


@st.cache_data
def load_csv(file_path):
    return pd.read_csv(file_path)

@st.cache_data
def load_csv_with_progress(file_path, chunksize=10000):
    logger = RotLogger()
    
    try:
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        progress_text = f"Loading {Path(file_path).name}"
        progress_bar = st.progress(0, text=progress_text)
        start_time = time.time()

        df = pd.read_csv(file_path)
        
        progress_bar.progress(100, text=f"✅ Loaded {len(df):,} rows, {len(df.columns)} columns")
        end_time = time.time()
        load_time = end_time - start_time
        
        logger.info(f"Loaded {len(df):,} rows and {len(df.columns)} columns in {load_time:.2f} seconds")
        time.sleep(0.5)
        progress_bar.empty()
        
        return df, load_time
        
    except Exception as e:
        logger.error(f"Error loading CSV: {e}")
        st.error(f"❌ Error loading file: {e}")
        return None

