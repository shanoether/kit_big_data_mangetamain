import streamlit as st
import polars as pl
from mangetamain.backend.helper import load_parquet_with_progress
from mangetamain.utils.logger import get_logger

st.set_page_config(
    page_title="Overview",
    page_icon="🔍",
    layout="centered",    
    initial_sidebar_state="expanded"
)
st.title("Data overview")

if 'data_loaded' in st.session_state and st.session_state.data_loaded:
    df_interactions = st.session_state.df_interactions
    df_recipes = st.session_state.df_recipes

    st.markdown("---")
    st.write("**Taille des datasets :**")

    col1, col2 = st.columns(2)
    col1.metric("Interactions", len(df_interactions))
    col2.metric("Recipes", len(df_recipes))

    st.subheader("Interactions (reviews)")
    st.write(df_interactions.head(10).to_pandas())

    st.subheader("Recipes")
    st.write(df_recipes.head(10).to_pandas())


