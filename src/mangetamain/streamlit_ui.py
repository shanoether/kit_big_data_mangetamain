import streamlit as st

from mangetamain.backend.helper import load_parquet_with_progress
from mangetamain.utils.logger import get_logger

logger = get_logger()

def main():

    if 'data_loaded' not in st.session_state:
        with st.spinner("🔄 Loading application data..."):
            logger.info("Application started, loading data.")
            st.session_state.df_interactions = load_parquet_with_progress("data/processed/processed_interactions.parquet")
            st.session_state.df_recipes = load_parquet_with_progress("data/processed/processed_recipes.parquet")
            st.session_state.data_loaded = True

    home_page = st.Page("frontend/pages/dashboard.py", title="Home", default=True)
    rating_page = st.Page("frontend/pages/rating.py", title="Rating")
    recipe_time_page = st.Page("frontend/pages/recipe_time.py", title="Recipe Time")
    
    pg = st.navigation(
        {
            "User": [home_page],
            "Analysis": [rating_page, recipe_time_page],
        }
    )
    

    pg.run()

if __name__ == "__main__":
    main()