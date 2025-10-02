import streamlit as st

from mangetamain.utils.logger import get_logger
from mangetamain.frontend.core.utils import load_csv_with_progress

logger = get_logger()

def main():

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    def login():
        if st.button("Log in"):
            st.session_state.logged_in = True
            st.rerun()

    def logout():
        if st.button("Log out"):
            st.session_state.logged_in = False
            st.rerun()

    login_page = st.Page(login, title="Log in", icon=":material/login:")
    logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

    if 'data_loaded' not in st.session_state:
        with st.spinner("🔄 Loading application data..."):
            st.session_state.df, st.session_state.load_time = load_csv_with_progress("data/RAW_interactions.csv")
            st.session_state.data_loaded = True

    home_page = st.Page("frontend/pages/dashboard.py", title="Home", default=True)
    rating_page = st.Page("frontend/pages/rating.py", title="Rating")
    recipe_time_page = st.Page("frontend/pages/recipe_time.py", title="Recipe Time")
    if st.session_state.logged_in:
        pg = st.navigation(
            {
                "User": [home_page, logout_page],
                "Analysis": [rating_page, recipe_time_page],
            }
        )
    else:
        pg = st.navigation(
            {
                "": [login_page],
            }
        )

    pg.run()

if __name__ == "__main__":
    main()