"""Unit tests for the backend helper functions."""

import io
import tempfile
import unittest
from unittest.mock import MagicMock, Mock, patch

import polars as pl
import streamlit as st

from mangetamain.utils.helper import (  # replace with actual module
    custom_exception_handler,
    load_csv_with_progress,
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

        # Clear Streamlit cache before running test
        st.cache_resource.clear()

        # Import function
        from mangetamain.utils.helper import load_data_from_parquet_and_pickle  # noqa PLC0415e

        # Act
        result = load_data_from_parquet_and_pickle()

        # Assert
        assert isinstance(result, tuple)
        assert len(result) == 11
        (
            df_interactions,
            _df_interactions_nna,
            _df_recipes,
            _df_recipes_nna,
            _df_total_nt,
            _df_total,
            _df_total_court,
            _proportion_m,
            _proportion_s,
            recipe_analyzer,
            data_loaded,
        ) = result

        assert data_loaded is True
        assert df_interactions.equals(mock_df)
        assert recipe_analyzer == mock_analyzer
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
        # Simulate missing file
        mock_load_parquet.side_effect = FileNotFoundError("File not found")

        # Clear Streamlit cache before running test
        st.cache_resource.clear()

        # Import function
        from mangetamain.utils.helper import load_data_from_parquet_and_pickle  # noqa PLC0415

        # Act
        result = load_data_from_parquet_and_pickle()

        # Assert
        assert isinstance(result, tuple)
        assert len(result) == 11
        data_loaded = result[10]  # Last element is data_loaded flag
        assert data_loaded is False
        mock_logger.error.assert_called_once()
        assert "Error loading data" in str(mock_logger.error.call_args)
        mock_st_error.assert_called_once()
        assert "Error loading data" in str(mock_st_error.call_args)

    @patch("mangetamain.backend.recipe_analyzer.RecipeAnalyzer.load")
    @patch("mangetamain.utils.helper.load_parquet_with_progress")
    @patch("mangetamain.utils.helper.logger")
    def test_load_data_pickle_load_error(
        self,
        mock_logger: MagicMock,
        mock_load_parquet: MagicMock,
        mock_recipe_analyzer_load: MagicMock,
    ) -> None:
        """Test that pickle loading errors are handled gracefully with fallback."""
        # Parquet files load OK, but pickle fails
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

        # Make RecipeAnalyzer.load raise an exception
        mock_recipe_analyzer_load.side_effect = OSError("Cannot read pickle file")

        # Clear Streamlit cache before running test
        st.cache_resource.clear()

        # Import function
        from mangetamain.utils.helper import load_data_from_parquet_and_pickle  # noqa PLC0415

        # Act
        result = load_data_from_parquet_and_pickle()

        # Assert
        assert isinstance(result, tuple)
        assert len(result) == 11
        recipe_analyzer = result[9]
        data_loaded = result[10]

        # Pickle error triggers fallback - data still loads with analyzer=None
        assert data_loaded is True
        assert recipe_analyzer is None
        mock_logger.warning.assert_called_once()
        assert "Failed to load pickle" in str(mock_logger.warning.call_args)

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
        # Simulate unexpected error
        mock_load_parquet.side_effect = RuntimeError("Unexpected error occurred")

        # Clear Streamlit cache before running test
        st.cache_resource.clear()

        # Import function
        from mangetamain.utils.helper import load_data_from_parquet_and_pickle  # noqa PLC0415

        # Act
        result = load_data_from_parquet_and_pickle()

        # Assert
        assert isinstance(result, tuple)
        assert len(result) == 11
        data_loaded = result[10]
        assert data_loaded is False
        mock_logger.error.assert_called_once()
        error_msg = str(mock_logger.error.call_args)
        assert "Unexpected error occurred" in error_msg
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
