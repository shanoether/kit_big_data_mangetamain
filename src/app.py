import streamlit as st

from utils.logger import get_logger

logger = get_logger()

def main():
    logger.info("this is main")

    test_page = st.Page("frontend/pages/test.py" ,title="Test")

    pg = st.navigation([test_page])

    pg.run()

if __name__ == "__main__":
    main()