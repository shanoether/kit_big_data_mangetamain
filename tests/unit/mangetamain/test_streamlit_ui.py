import unittest
from unittest.mock import patch, MagicMock
import streamlit as st

from mangetamain.streamlit_ui import load_data_from_parquet, main

class TestStreamlitUI(unittest.TestCase):
    @patch("mangetamain.streamlit_ui.load_parquet_with_progress")
    @patch("mangetamain.streamlit_ui.logger")
    def test_load_data_from_parquet(self, mock_logger, mock_load_parquet):
        # Mock return values for each parquet file
        mock_load_parquet.side_effect = [
            {"dummy": 1},  # df_interactions
            {"dummy": 2},  # df_recipes
            {"dummy": 3},  # df_total
            {"dummy": 4},  # df_total_court
            {"proportion_m": [0.1, 0.2]},  # proportion_m
            {"proportion_s": [0.3, 0.4]},  # proportion_s
        ]

        # Clear session state
        st.session_state.clear()

        load_data_from_parquet()

        # Verify st.session_state is populated
        self.assertIn("df_interactions", st.session_state)
        self.assertIn("df_recipes", st.session_state)
        self.assertIn("df_total", st.session_state)
        self.assertIn("df_total_court", st.session_state)
        self.assertIn("proportion_m", st.session_state)
        self.assertIn("proportion_s", st.session_state)
        self.assertTrue(st.session_state.data_loaded)

        # Logger info called
        mock_logger.info.assert_called_with("Data loaded into session state.")

    @patch("mangetamain.streamlit_ui.st")
    @patch("mangetamain.streamlit_ui.load_data_from_parquet")
    @patch("mangetamain.streamlit_ui.logger")
    def test_main_calls_data_loading_and_navigation(self, mock_logger, mock_load_data, mock_st):
        # Simulate empty session_state
        mock_st.session_state = {}

        # Mock pages and navigation
        mock_st.Page = MagicMock()
        mock_pg = MagicMock()
        mock_st.navigation.return_value = mock_pg

        main()

        # Ensure data loading was called
        mock_load_data.assert_called_once()

        # Ensure pages are instantiated
        self.assertTrue(mock_st.Page.called)

        # Ensure navigation run was called
        mock_pg.run.assert_called_once()

        # Logger info should be called at startup
        mock_logger.info.assert_any_call("Application started, loading data.")

if __name__ == "__main__":
    unittest.main()
