"""Main entry point for the Streamlit UI application and doing the dispatch between the pages."""

import cProfile
import pstats
import sys
import time

import streamlit as st
from streamlit_extras.exception_handler import set_global_exception_handler

from mangetamain.utils.helper import (
    custom_exception_handler,
    load_data_from_parquet_and_pickle,
)
from mangetamain.utils.logger import get_logger

logger = get_logger()

set_global_exception_handler(custom_exception_handler)

st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] li a {
        font-size: 1.1rem !important;  /* mặc định ~0.9rem */
        padding: 10px 16px !important;
    }

    [data-testid="stSidebarNav"] li a span {
        font-size: 1.3rem !important;
    }

    [data-testid="stSidebarNav"] li a {
        font-weight: 600 !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)


def main() -> None:
    """Entry point for the Streamlit front-end application.

    This function prepares the navigation pages and ensures the
    application data is loaded into the Streamlit session state before
    starting the page navigation.

    The data loading is optimized with @st.cache_resource:
    - First user: ~90s to load all data
    - All subsequent users: <0.01s (instant cache hit)
    """
    # Always call the cached function (it returns instantly after first call)
    cache_start = time.time()
    (
        df_interactions,
        df_interactions_nna,
        df_recipes,
        df_recipes_nna,
        df_total_nt,
        df_total,
        df_total_court,
        proportion_m,
        proportion_s,
        recipe_analyzer,
        data_loaded,
    ) = load_data_from_parquet_and_pickle()
    cache_time = time.time() - cache_start

    logger.info(f"⚡ Cache access took {cache_time:.4f}s")

    # Store in session_state ONCE per user for convenience
    if "data_loaded" not in st.session_state:
        with st.spinner("🔄 Loading application data..."):
            logger.info("Storing data in session_state for this user.")
            st.session_state.df_interactions = df_interactions
            st.session_state.df_interactions_nna = df_interactions_nna
            st.session_state.df_recipes = df_recipes
            st.session_state.df_recipes_nna = df_recipes_nna
            st.session_state.df_total_nt = df_total_nt
            st.session_state.df_total = df_total
            st.session_state.df_total_court = df_total_court
            st.session_state.proportion_m = proportion_m
            st.session_state.proportion_s = proportion_s
            st.session_state.recipe_analyzer = recipe_analyzer
            st.session_state.data_loaded = data_loaded
            logger.info("✅ Data available in session_state for this user.")

    home_page = st.Page("frontend/pages/dashboard.py", title="🏠 Home", default=True)
    # overview_page = st.Page("frontend/pages/overview.py", title="📊 Overview")
    recipes_analysis_page = st.Page(
        "frontend/pages/recipes_analysis.py",
        title="🍳 Recipes",
    )
    users_analysis_page = st.Page("frontend/pages/users_analysis.py", title="👥 Users")
    trends_page = st.Page("frontend/pages/trends.py", title="📈 Trends")
    rating_page = st.Page("frontend/pages/rating.py", title="⭐ Rating")
    # recipe_time_page = st.Page("frontend/pages/recipes_analysis.py", title="Recipe Time")

    pg = st.navigation(
        [
            home_page,
            # overview_page,
            rating_page,
            trends_page,
            users_analysis_page,
            recipes_analysis_page,
        ],
    )

    pg.run()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "profile":
        cProfile.run("main()", filename="docs/streamlit_profile.prof")
        stats = pstats.Stats("docs/streamlit_profile.prof")
        stats.strip_dirs().sort_stats("cumulative").print_stats(10)
    else:
        main()
