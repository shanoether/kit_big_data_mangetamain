"""Dashboard page for the Mangetamain Streamlit app."""

import streamlit as st

from mangetamain.utils.logger import get_logger

logger = get_logger()

st.set_page_config(
    page_title="Mangetamain Analysis App",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(
    """
    <style>
    p { font-size: 1.2rem !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.success("📂 Select a page to navigate")

st.title("🏠 Mangetamain v1.0")

st.markdown(
    """
    <div style="text-align: justify;">
    <p>
    Mangetamain Garde l'autre pour demain Analysis App - Main Page

    Welcome to Mangetamain v1.0, your interactive platform for exploring recipes and user interactions.
    This main page serves as the starting point of the app, providing guidance on navigation and an overview of the project.
    Use the sidebar to move between different sections and explore analyses.
    Once the data is loaded, you'll see a confirmation of the number of interactions available,
    giving you a quick sense of the dataset's size. This page sets the stage for deeper insights into user reviews,
    recipe characteristics, and contributor activity throughout the app.
    </p>
    </div>
    """,
    unsafe_allow_html=True,
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
        """
        <div style="text-align: justify;">
        <p>
        This page provides a general overview of the datasets used in the application.
        It shows key information about user interactions (reviews) and recipes.
        You can see the size of each dataset and a sample of the first rows to get a sense of their structure and content.
        This step is essential to understand the data before performing univariate and bivariate analyses,
        and serves as a starting point to explore review trends, contributor activity, and recipe characteristics.
        </p>
        </div>""",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.subheader("📦 Dataset Summary")

    col1, spacer, col2 = st.columns([1, 0.1, 1])
    col1.metric("User Interactions", f"{len(df_interactions):,}")
    col2.metric("Recipes", f"{len(df_recipes):,}")
    col1.markdown("---")
    col2.markdown("---")

    # st.markdown("---")
    col1, spacer, col2 = st.columns([1, 0.1, 1])
    with col1:
        st.subheader("👥 Interactions (reviews) Sample")
        st.write(df_interactions.head(10).to_pandas())

    with col2:
        st.subheader("🍳 Recipes Sample")
        st.write(df_recipes.head(10).to_pandas())
else:
    st.error("❌ Data not loaded properly. Please refresh the page.")
