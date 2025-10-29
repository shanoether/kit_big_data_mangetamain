"""Dashboard page for the Mangetamain Streamlit app."""

import streamlit as st

from mangetamain.utils.logger import get_logger

logger = get_logger()

st.set_page_config(
    page_title="Mangetamain Analysis App",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.sidebar.success("Select a page to navigate.")

st.title("Mangetamain 🏠 v1.6")

st.write("Welcome to the main page!")
st.write("Use the sidebar to navigate to different sections of the app.")
st.write("Below is the information about the project")

if "data_loaded" in st.session_state and st.session_state.data_loaded:
    df_interactions = st.session_state.df_interactions
    df_recipes = st.session_state.df_recipes
    st.success(
        f"✅ Successfully loaded {len(df_interactions):,} interactions and {len(df_recipes):,} recipes.",
    )
    df_interactions = st.session_state.df_interactions
    df_recipes = st.session_state.df_recipes

    st.markdown("---")
    st.write("**Dataset sizes:**")

    col1, col2 = st.columns(2)
    col1.metric("Interactions", len(df_interactions))
    col2.metric("Recipes", len(df_recipes))

    st.subheader("Interactions (reviews)")
    st.write(df_interactions.head(10).to_pandas())

    st.subheader("Recipes")
    st.write(df_recipes.head(10).to_pandas())
else:
    st.error("❌ Data not loaded properly. Please refresh the page.")
