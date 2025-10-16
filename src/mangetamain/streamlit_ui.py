import streamlit as st

from mangetamain.backend.helper import load_parquet_with_progress
from mangetamain.utils.logger import get_logger

logger = get_logger()


def load_data_from_parquet():
    """Load data from parquet files into session state."""
    
    st.session_state.df_interactions = load_parquet_with_progress("data/processed/processed_interactions.parquet")
    st.session_state.df_recipes = load_parquet_with_progress("data/processed/processed_recipes.parquet")
    st.session_state.df_total = load_parquet_with_progress("data/processed/total.parquet")    
    st.session_state.df_total_court = load_parquet_with_progress("data/processed/short.parquet")
    st.session_state.proportion_m = load_parquet_with_progress("data/processed/proportion_m.parquet")["proportion_m"]
    st.session_state.proportion_s = load_parquet_with_progress("data/processed/proportion_s.parquet")["proportion_s"]
    st.session_state.data_loaded = True
    logger.info("Data loaded into session state.")

def main():

    if 'data_loaded' not in st.session_state:
        with st.spinner("🔄 Loading application data..."):
            logger.info("Application started, loading data.")
            load_data_from_parquet()

    home_page = st.Page("frontend/pages/dashboard.py", title="Home", default=True)
    rating_page = st.Page("frontend/pages/rating.py", title="Rating")
    #recipe_time_page = st.Page("frontend/pages/recipes_analysis.py", title="Recipe Time")
    overview_page = st.Page("frontend/pages/overview.py", title="Overview")
    recipes_analysis_page = st.Page("frontend/pages/recipes_analysis.py", title="Recipes Analysis")
    users_analysis_page = st.Page("frontend/pages/users_analysis.py", title="Users Analysis")
    trends_page = st.Page("frontend/pages/trends.py", title="Trends")
    
    pg = st.navigation(
        {
            "User": [home_page],
            "Analysis": [overview_page, recipes_analysis_page, users_analysis_page, trends_page, rating_page],
        }
    )
    

    pg.run()

if __name__ == "__main__":
    main()