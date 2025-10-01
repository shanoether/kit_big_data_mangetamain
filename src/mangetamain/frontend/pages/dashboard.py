import streamlit as st

from mangetamain.utils.logger import RotLogger
from mangetamain.frontend.core.utils import load_csv_with_progress
from mangetamain.frontend.core.data_processor import DataProcessor

st.set_page_config(
    page_title="Mangetamain Analysis App",
    page_icon="🍳",
    initial_sidebar_state="expanded"
)
st.sidebar.success("Select a page to navigate.")

st.title("Mangetamain 🏠")

st.write("Welcome to the main page!")
st.write("Use the sidebar to navigate to different sections of the app.")
st.write("Below is the information about the project")

if 'data_loaded' in st.session_state and st.session_state.data_loaded:
    df = st.session_state.data_processor.get_data()
    load_time = st.session_state.load_time
    
    st.success(f"✅ Successfully loaded {len(df):,} interactions in {load_time:.2f} seconds")
else:
    st.error("❌ Data not loaded properly. Please refresh the page.")