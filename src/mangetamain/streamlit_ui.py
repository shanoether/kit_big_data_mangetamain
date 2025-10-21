"""Main entry point for the Streamlit UI application and doing the dispatch between the pages."""

import streamlit as st

from mangetamain.backend.recipe_analyzer import RecipeAnalyzer  
from mangetamain.backend.helper import load_parquet_with_progress
from mangetamain.utils.logger import get_logger

logger = get_logger()


def load_data_from_parquet() -> None:
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
    st.session_state.df_interactions = load_parquet_with_progress(
        "data/processed/processed_interactions.parquet",
    )
    st.session_state.df_recipes = load_parquet_with_progress(
        "data/processed/processed_recipes.parquet",
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
    
    st.session_state.recipe_analyzer = RecipeAnalyzer(st.session_state.df_interactions, st.session_state.df_recipes)

    st.session_state.data_loaded = True
    
    logger.info("Data loaded into session state.")


def main() -> None:
    """Entry point for the Streamlit front-end application.

    This function prepares the navigation pages and ensures the
    application data is loaded into the Streamlit session state before
    starting the page navigation.
    """
    if "data_loaded" not in st.session_state:
        with st.spinner("🔄 Loading application data..."):
            logger.info("Application started, loading data.")
            load_data_from_parquet()

    home_page = st.Page("frontend/pages/dashboard.py", title="Home", default=True)
    rating_page = st.Page("frontend/pages/rating.py", title="Rating")
    # recipe_time_page = st.Page("frontend/pages/recipes_analysis.py", title="Recipe Time")
    overview_page = st.Page("frontend/pages/overview.py", title="Overview")
    recipes_analysis_page = st.Page(
        "frontend/pages/recipes_analysis.py",
        title="Recipes Analysis",
    )
    users_analysis_page = st.Page(
        "frontend/pages/users_analysis.py",
        title="Users Analysis",
    )
    trends_page = st.Page("frontend/pages/trends.py", title="Trends")

    pg = st.navigation(
        [
            home_page,
            overview_page,
            recipes_analysis_page,
            users_analysis_page,
            trends_page,
            rating_page
        ],
    )

    pg.run()


if __name__ == "__main__":
    main()
