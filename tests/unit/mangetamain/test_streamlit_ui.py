"""Unit tests for the Streamlit UI module."""

import unittest
from typing import Any
from unittest.mock import MagicMock, patch

from mangetamain.streamlit_ui import main


class MockSessionState:
    """Mock session_state that supports both attribute and dict-style access."""

    def __init__(self) -> None:
        """Initialize the mock session state with an empty data dictionary."""
        self._data: dict[str, Any] = {}

    def __setattr__(self, name: str, value: Any) -> None:  # noqa: ANN401
        """Set attribute, storing in internal dict unless it's _data itself."""
        if name == "_data":
            super().__setattr__(name, value)
        else:
            self._data[name] = value

    def __getattr__(self, name: str) -> Any:  # noqa: ANN401
        """Get attribute from internal dict."""
        if name == "_data":
            return super().__getattribute__(name)
        return self._data.get(name)

    def __contains__(self, key: str) -> bool:
        """Check if key exists in internal dict."""
        return key in self._data

    def __getitem__(self, key: str) -> Any:  # noqa: ANN401
        """Get item from internal dict using dict-style access."""
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:  # noqa: ANN401
        """Set item in internal dict using dict-style access."""
        self._data[key] = value


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
        # Mock the return value of load_data_from_parquet_and_pickle (tuple of 11 elements)
        mock_load_data.return_value = (
            MagicMock(),  # df_interactions
            MagicMock(),  # df_interactions_nna
            MagicMock(),  # df_recipes
            MagicMock(),  # df_recipes_nna
            MagicMock(),  # df_total_nt
            MagicMock(),  # df_total
            MagicMock(),  # df_total_court
            MagicMock(),  # proportion_m
            MagicMock(),  # proportion_s
            MagicMock(),  # recipe_analyzer
            True,  # data_loaded
        )

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

        # Logger should log cache access time and data storage
        assert mock_logger.info.called

    @patch("mangetamain.streamlit_ui.st")
    @patch("mangetamain.streamlit_ui.load_data_from_parquet_and_pickle")
    @patch("mangetamain.streamlit_ui.logger")
    def test_main_stores_data_in_session_state(
        self,
        mock_logger: MagicMock,
        mock_load_data: MagicMock,
        mock_st: MagicMock,
    ) -> None:
        """Test that main function stores all data in session_state when not present."""
        # Create mock data
        mock_df_interactions = MagicMock()
        mock_df_interactions_nna = MagicMock()
        mock_df_recipes = MagicMock()
        mock_df_recipes_nna = MagicMock()
        mock_df_total_nt = MagicMock()
        mock_df_total = MagicMock()
        mock_df_total_court = MagicMock()
        mock_proportion_m = MagicMock()
        mock_proportion_s = MagicMock()
        mock_recipe_analyzer = MagicMock()

        # Mock the return value of load_data_from_parquet_and_pickle
        mock_load_data.return_value = (
            mock_df_interactions,
            mock_df_interactions_nna,
            mock_df_recipes,
            mock_df_recipes_nna,
            mock_df_total_nt,
            mock_df_total,
            mock_df_total_court,
            mock_proportion_m,
            mock_proportion_s,
            mock_recipe_analyzer,
            True,
        )

        # Start with empty session_state (data_loaded not present)
        mock_session_state = MockSessionState()
        mock_st.session_state = mock_session_state

        # Mock spinner context manager
        mock_spinner = MagicMock()
        mock_spinner.__enter__ = MagicMock(return_value=mock_spinner)
        mock_spinner.__exit__ = MagicMock(return_value=False)
        mock_st.spinner.return_value = mock_spinner

        # Mock pages and navigation
        mock_st.Page = MagicMock()
        mock_pg = MagicMock()
        mock_st.navigation.return_value = mock_pg

        # Call main
        main()

        # Verify all data was stored in session_state
        assert mock_session_state["df_interactions"] == mock_df_interactions
        assert mock_session_state["df_interactions_nna"] == mock_df_interactions_nna
        assert mock_session_state["df_recipes"] == mock_df_recipes
        assert mock_session_state["df_recipes_nna"] == mock_df_recipes_nna
        assert mock_session_state["df_total_nt"] == mock_df_total_nt
        assert mock_session_state["df_total"] == mock_df_total
        assert mock_session_state["df_total_court"] == mock_df_total_court
        assert mock_session_state["proportion_m"] == mock_proportion_m
        assert mock_session_state["proportion_s"] == mock_proportion_s
        assert mock_session_state["recipe_analyzer"] == mock_recipe_analyzer
        assert mock_session_state["data_loaded"] is True

        # Verify spinner was used
        mock_st.spinner.assert_called_once_with("🔄 Loading application data...")

        # Verify logging messages
        mock_logger.info.assert_any_call("Storing data in session_state for this user.")
        mock_logger.info.assert_any_call(
            "✅ Data available in session_state for this user.",
        )

    @patch("mangetamain.streamlit_ui.st")
    @patch("mangetamain.streamlit_ui.load_data_from_parquet_and_pickle")
    @patch("mangetamain.streamlit_ui.logger")
    def test_main_skips_storage_when_data_already_loaded(
        self,
        mock_logger: MagicMock,
        mock_load_data: MagicMock,
        mock_st: MagicMock,
    ) -> None:
        """Test that main function skips session_state storage when data_loaded is present."""
        # Mock the return value
        mock_load_data.return_value = (
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            True,
        )

        # Simulate session_state already having data_loaded
        mock_session_state = MockSessionState()
        mock_session_state.data_loaded = True
        mock_st.session_state = mock_session_state

        # Mock pages and navigation
        mock_st.Page = MagicMock()
        mock_pg = MagicMock()
        mock_st.navigation.return_value = mock_pg

        # Call main
        main()

        # Verify spinner was NOT called (no storage operation)
        mock_st.spinner.assert_not_called()

        # Verify the storage log messages were NOT called
        info_calls = [str(call) for call in mock_logger.info.call_args_list]
        assert not any("Storing data in session_state" in call for call in info_calls)


if __name__ == "__main__":
    unittest.main()
