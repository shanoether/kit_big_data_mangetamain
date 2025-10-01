import streamlit as st

from mangetamain.utils.logger import RotLogger 
from mangetamain.frontend.core.utils import load_csv_with_progress
from mangetamain.frontend.core.data_processor import DataProcessor

def main():
    if 'data_loaded' not in st.session_state:
        with st.spinner("🔄 Loading application data..."):
            df, st.session_state.load_time = load_csv_with_progress("data/RAW_interactions.csv")
            st.session_state.data_processor = DataProcessor()
            st.session_state.data_processor.set_data(df)
            st.session_state.data_loaded = True

    home_page = st.Page("frontend/pages/dashboard.py", title="Home", default=True)
    rating_page = st.Page("frontend/pages/rating.py", title="Rating")
    recipe_time_page = st.Page("frontend/pages/recipe_time.py", title="Recipe Time")
    pg = st.navigation(
        {
            "": [home_page],
            "Analysis": [rating_page, recipe_time_page],
        }
    )

    pg.run()

if __name__ == "__main__":
    main()