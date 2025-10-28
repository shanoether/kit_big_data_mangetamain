"""Unit tests for the Streamlit UI module."""

import unittest
from unittest.mock import MagicMock, patch

from mangetamain.streamlit_ui import main


class TestStreamlitUI(unittest.TestCase):
    """Unit tests for the Streamlit UI functions."""

    # Moved to test_helper.py
    # @patch("mangetamain.streamlit_ui.load_parquet_with_progress")
    # @patch("mangetamain.streamlit_ui.logger")
    # def test_load_data_from_parquet(
    #     self,
    #     mock_logger: MagicMock,
    #     mock_load_parquet: MagicMock,
    # ) -> None:
    #     """Test loading data from parquet files into Streamlit session state."""
    #     # Mock return values for each parquet file
    #     mock_load_parquet.side_effect = [
    #         {"dummy": 1},  # df_interactions
    #         {"dummy": 2},  # df_recipes
    #         {"dummy": 3},  # df_total
    #         {"dummy": 4},  # df_total_court
    #         {"dummy": 5},  # df_interactions_nna
    #         {"dummy": 6},  # df_recipes_nna
    #         {"dummy": 7},  # df_recipes_nna
    #         {"proportion_m": [0.1, 0.2]},  # proportion_m
    #         {"proportion_s": [0.3, 0.4]},  # proportion_s
    #     ]

    #     # Clear session state
    #     st.session_state.clear()

    #     load_data_from_parquet()

    #     # Verify st.session_state is populated
    #     assert "df_interactions" in st.session_state
    #     assert "df_recipes" in st.session_state
    #     assert "df_total" in st.session_state
    #     assert "df_total_court" in st.session_state
    #     assert "proportion_m" in st.session_state
    #     assert "proportion_s" in st.session_state
    #     assert st.session_state.data_loaded

    #     # Logger info called
    #     mock_logger.info.assert_called_with("Data loaded into session state.")

    @patch("mangetamain.streamlit_ui.st")
    @patch("mangetamain.streamlit_ui.load_data_from_parquet_and_pickle")
    @patch("mangetamain.streamlit_ui.logger")
    def test_main_calls_data_loading_and_navigation(
        self,
        mock_logger: MagicMock,
        mock_load_data: MagicMock,
        mock_st: MagicMock,
    ) -> None:
        """Test that main function loads data and sets up navigation."""
        # Simulate empty session_state
        mock_st.session_state = {}

        # Mock pages and navigation
        mock_st.Page = MagicMock()
        mock_pg = MagicMock()
        mock_st.navigation.return_value = mock_pg
        mock_st.spinner = MagicMock()
        mock_st.spinner.return_value.__enter__ = MagicMock()
        mock_st.spinner.return_value.__exit__ = MagicMock()

        main()

        # Ensure data loading was called
        mock_load_data.assert_called_once()

        # Ensure pages are instantiated
        assert mock_st.Page.called

        # Ensure navigation run was called
        mock_pg.run.assert_called_once()

        # Logger info should be called at startup
        mock_logger.info.assert_any_call("Application started, loading data.")


if __name__ == "__main__":
    unittest.main()
