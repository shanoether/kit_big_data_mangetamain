"""Unit tests for the backend helper functions."""

import io
import tempfile
import unittest

import polars as pl

from mangetamain.backend.helper import (  # replace with actual module
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


if __name__ == "__main__":
    unittest.main()
