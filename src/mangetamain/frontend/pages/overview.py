"""Overview page of the Streamlit app."""

import streamlit as st

st.set_page_config(
    page_title="Overview",
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

st.title("📊 Data Overview")

st.markdown("""
This page provides an overview of the core datasets used in Mangetamain.
You can inspect data sizes and preview sample rows from both interactions and recipes.
""")

if "data_loaded" in st.session_state and st.session_state.data_loaded:
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
    st.warning("❌ Data not loaded properly. Please refresh the page.")
