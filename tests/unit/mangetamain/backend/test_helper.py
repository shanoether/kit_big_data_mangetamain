import unittest
import polars as pl
from mangetamain.backend.helper import load_csv_with_progress, load_parquet_with_progress  # replace with actual module

class TestHelper(unittest.TestCase):

    def test_load_csv_basic(self):
        # Create a simple CSV in-memory using StringIO
        import io
        csv_data = io.StringIO("a,b\n1,x\n2,y\n3,z")
        df, load_time = load_csv_with_progress(csv_data)
        self.assertIsInstance(df, pl.DataFrame)
        self.assertEqual(df.shape[0], 3)
        self.assertEqual(df.shape[1], 2)

    def test_load_parquet_basic(self):
        # Create a simple DataFrame and write to Parquet in-memory
        import tempfile
        df_input = pl.DataFrame({"a": [1,2], "b": ["x","y"]})
        with tempfile.NamedTemporaryFile(suffix=".parquet") as f:
            df_input.write_parquet(f.name)
            df = load_parquet_with_progress(f.name)
        self.assertIsInstance(df, pl.DataFrame)
        self.assertEqual(df.shape, df_input.shape)

if __name__ == "__main__":
    unittest.main()
