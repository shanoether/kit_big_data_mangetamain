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

st.title("Mangetamain 🏠 v1.0")

st.write("Welcome to the main page!")
st.write("Use the sidebar to navigate to different sections of the app.")
st.write(
    "Mangetamain Garde l'autre pour demain Analysis App - Main Page\
Welcome to Mangetamain v1.0, your interactive platform for exploring recipes and user interactions. This main page serves as the starting point of the app, providing guidance on navigation and an overview of the project.\
Use the sidebar to move between different sections and explore analyses. Once the data is loaded, you'll see a confirmation of the number of interactions available, giving you a quick sense of the dataset's size. This page sets the stage for deeper insights into user reviews, recipe characteristics, and contributor activity throughout the app.",
)

if "data_loaded" in st.session_state and st.session_state.data_loaded:
    df_interactions = st.session_state.df_interactions
    df_recipes = st.session_state.df_recipes
    st.success(
        f"✅ Successfully loaded {len(df_interactions):,} interactions and {len(df_recipes):,} recipes.",
    )
    df_interactions = st.session_state.df_interactions
    df_recipes = st.session_state.df_recipes

    st.markdown("---")
    st.markdown(
        "This page provides a general overview of the datasets used in the application. It shows key information about user interactions (reviews) and recipes. You can see the size of each dataset and a sample of the first rows to get a sense of their structure and content. This step is essential to understand the data before performing univariate and bivariate analyses, and serves as a starting point to explore review trends, contributor activity, and recipe characteristics.",
    )
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
