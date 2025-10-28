"""Main entry point for the Streamlit UI application and doing the dispatch between the pages."""

import cProfile
import pstats
import sys

import streamlit as st
from streamlit_extras.exception_handler import set_global_exception_handler

from mangetamain.utils.helper import (
    custom_exception_handler,
    load_data_from_parquet_and_pickle,
)
from mangetamain.utils.logger import get_logger

logger = get_logger()

set_global_exception_handler(custom_exception_handler)


def main() -> None:
    """Entry point for the Streamlit front-end application.

    This function prepares the navigation pages and ensures the
    application data is loaded into the Streamlit session state before
    starting the page navigation.
    """
    if "data_loaded" not in st.session_state:
        with st.spinner("🔄 Loading application data..."):
            logger.info("Application started, loading data.")
            load_data_from_parquet_and_pickle()

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
            rating_page,
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
