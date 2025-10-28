"""Unit tests for the backend helper functions."""

import io
import tempfile
import unittest
from unittest.mock import MagicMock, Mock, mock_open, patch

import polars as pl
import streamlit as st

from mangetamain.utils.helper import (  # replace with actual module
    custom_exception_handler,
    load_csv_with_progress,
    load_data_from_parquet_and_pickle,
    load_parquet_with_progress,
)


class TestHelper(unittest.TestCase):
    """Unit tests for the backend helper functions."""

    def test_load_csv_basic(self) -> None:
        """Test loading a simple CSV file."""
        # Create a simple CSV in-memory using StringIO

        csv_data = io.StringIO("a,b\n1,x\n2,y\n3,z")
        df, _ = load_csv_with_progress(csv_data)
        assert isinstance(df, pl.DataFrame)
        assert df.shape[0] == 3
        assert df.shape[1] == 2

    def test_load_parquet_basic(self) -> None:
        """Test loading a simple Parquet file."""
        # Create a simple DataFrame and write to Parquet in-memory

        df_input = pl.DataFrame({"a": [1, 2], "b": ["x", "y"]})
        with tempfile.NamedTemporaryFile(suffix=".parquet") as f:
            df_input.write_parquet(f.name)
            df = load_parquet_with_progress(f.name)

        assert isinstance(df, pl.DataFrame)
        assert df.shape == df_input.shape

    @patch("mangetamain.backend.recipe_analyzer.RecipeAnalyzer.load")
    @patch("mangetamain.utils.helper.load_parquet_with_progress")
    def test_load_data_success(
        self,
        mock_load_parquet: MagicMock,
        mock_recipe_analyzer_load: MagicMock,
    ) -> None:
        """Test successful loading of all data files."""
        # Arrange
        mock_df = pl.DataFrame({"col1": [1, 2, 3]})
        mock_series = pl.Series("test", [0.1, 0.2, 0.3])

        # Mock all parquet loads
        mock_load_parquet.side_effect = [
            mock_df,  # initial_interactions
            mock_df,  # processed_interactions
            mock_df,  # initial_recipes
            mock_df,  # processed_recipes
            mock_df,  # total_nt
            mock_df,  # total
            mock_df,  # short
            pl.DataFrame({"proportion_m": mock_series}),  # proportion_m
            pl.DataFrame({"proportion_s": mock_series}),  # proportion_s
        ]

        # Mock RecipeAnalyzer.load
        mock_analyzer = MagicMock()
        mock_recipe_analyzer_load.return_value = mock_analyzer

        # Act
        result = load_data_from_parquet_and_pickle()

        # Assert
        assert result is True
        assert st.session_state.data_loaded is True
        assert st.session_state.df_interactions.equals(mock_df)
        assert st.session_state.recipe_analyzer == mock_analyzer
        assert mock_load_parquet.call_count == 9
        mock_recipe_analyzer_load.assert_called_once_with(
            "data/processed/recipe_analyzer.pkl",
        )

    @patch("mangetamain.utils.helper.load_parquet_with_progress")
    @patch("mangetamain.utils.helper.logger")
    @patch("streamlit.error")
    def test_load_data_file_not_found_error(
        self,
        mock_st_error: MagicMock,
        mock_logger: MagicMock,
        mock_load_parquet: MagicMock,
    ) -> None:
        """Test that FileNotFoundError is handled gracefully."""
        # Arrange: Simulate missing file
        mock_load_parquet.side_effect = FileNotFoundError("File not found")

        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]

        # Act
        result = load_data_from_parquet_and_pickle()

        # Assert
        assert result is False
        assert st.session_state.data_loaded is False
        mock_logger.error.assert_called_once()
        assert "Error loading data" in str(mock_logger.error.call_args)
        mock_st_error.assert_called_once()
        assert "Error loading data" in str(mock_st_error.call_args)

    @patch("mangetamain.utils.helper.load_parquet_with_progress")
    @patch("builtins.open", new_callable=mock_open)
    @patch("mangetamain.utils.helper.logger")
    @patch("streamlit.error")
    def test_load_data_pickle_load_error(
        self,
        mock_st_error: MagicMock,
        mock_logger: MagicMock,
        mock_file_open: MagicMock,
        mock_load_parquet: MagicMock,
    ) -> None:
        """Test that pickle loading errors are handled gracefully."""
        # Arrange: Parquet files load OK, but pickle fails
        mock_df = pl.DataFrame({"col1": [1, 2, 3]})
        mock_series = pl.Series("test", [0.1, 0.2, 0.3])

        mock_load_parquet.side_effect = [
            mock_df,  # initial_interactions
            mock_df,  # processed_interactions
            mock_df,  # initial_recipes
            mock_df,  # processed_recipes
            mock_df,  # total_nt
            mock_df,  # total
            mock_df,  # short
            pl.DataFrame({"proportion_m": mock_series}),
            pl.DataFrame({"proportion_s": mock_series}),
        ]

        # Make open() raise an exception when reading pickle
        mock_file_open.side_effect = OSError("Cannot read pickle file")

        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]

        # Act
        result = load_data_from_parquet_and_pickle()

        # Assert
        assert result is False
        assert st.session_state.data_loaded is False
        mock_logger.error.assert_called_once()
        assert "Cannot read pickle file" in str(mock_logger.error.call_args)
        mock_st_error.assert_called_once()

    @patch("mangetamain.utils.helper.load_parquet_with_progress")
    @patch("mangetamain.utils.helper.logger")
    @patch("streamlit.error")
    def test_load_data_generic_exception(
        self,
        mock_st_error: MagicMock,
        mock_logger: MagicMock,
        mock_load_parquet: MagicMock,
    ) -> None:
        """Test that any generic exception is caught and logged."""
        # Arrange: Simulate unexpected error
        mock_load_parquet.side_effect = RuntimeError("Unexpected error occurred")

        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]

            # Act
            result = load_data_from_parquet_and_pickle()

            # Assert
            assert result is False
            assert st.session_state.data_loaded is False
            mock_logger.error.assert_called_once()
            error_msg = str(mock_logger.error.call_args)
            assert "Unexpected error occurred" in error_msg
            assert "please run backend/dataprocessor first" in error_msg.lower()
            mock_st_error.assert_called_once()

    # Tests for custom_exception_handler function
    @patch("streamlit.error")
    @patch("mangetamain.utils.logger.get_logger")
    def test_exception_handler_logs_and_displays(
        self,
        mock_get_logger: MagicMock,
        mock_st_error: MagicMock,
    ) -> None:
        """Test that exception handler logs error and displays user message."""
        # Arrange
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        test_exception = ValueError("Test error message")

        # Act
        custom_exception_handler(test_exception)

        # Assert
        mock_logger.error.assert_called_once()
        assert "Test error message" in str(mock_logger.error.call_args)
        mock_st_error.assert_called_once_with(
            "An unexpected error occurred. Please contact support.",
        )


if __name__ == "__main__":
    unittest.main()
