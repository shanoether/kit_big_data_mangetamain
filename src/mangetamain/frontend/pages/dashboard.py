import streamlit as st

from mangetamain.utils.logger import get_logger
logger = get_logger()

st.set_page_config(
    page_title="Mangetamain Analysis App",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.sidebar.success("Select a page to navigate.")

st.title("Mangetamain 🏠")

st.write("Welcome to the main page!")
st.write("Use the sidebar to navigate to different sections of the app.")
st.write("Below is the information about the project")

if 'data_loaded' in st.session_state and st.session_state.data_loaded:
    df = st.session_state.df
    load_time = st.session_state.load_time
    
    st.success(f"✅ Successfully loaded {len(df):,} interactions in {load_time:.2f} seconds")
else:
    st.error("❌ Data not loaded properly. Please refresh the page.")