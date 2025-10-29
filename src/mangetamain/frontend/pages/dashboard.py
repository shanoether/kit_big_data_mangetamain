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

st.title("🏠 Mangetamain v1.6")

st.markdown("""
Welcome to **MangeTaMain**!

Use the sidebar to navigate through different sections of the app.
Below is a quick summary of your currently loaded data.
Click the zoom button at the top-right corner
of each image to view it more clearly.
""")

if "data_loaded" in st.session_state and st.session_state.data_loaded:
    df_interactions = st.session_state.df_interactions
    df_recipes = st.session_state.df_recipes
    st.success(
        f"✅ Successfully loaded {len(df_interactions):,} interactions and {len(df_recipes):,} recipes.",
    )
    df_interactions = st.session_state.df_interactions
    df_recipes = st.session_state.df_recipes

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
