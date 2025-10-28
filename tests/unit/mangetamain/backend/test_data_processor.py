"""Unit tests for the DataProcessor module."""

# tests/unit/mangetamain/backend/test_dataprocessor.py
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import polars as pl
import pytest

from mangetamain.backend.data_processor import DataProcessor


class TestDataProcessor:
    """Tests complets pour le module DataProcessor."""

    @pytest.fixture(autouse=True)  # type: ignore
    def setup(self, tmp_path: Path) -> None:
        """Créer des fichiers CSV temporaires et initialiser DataProcessor."""
        # Interactions CSV
        self.interactions_csv = tmp_path / "RAW_interactions.csv"
        self.interactions_csv.write_text(
            "user_id,recipe_id,rating,review,date\n"
            "1,101,5,Great,2023-01-01\n"
            "2,102,4,,2023-01-02\n"  # NA review
            "3,103,5,Excellent,2023-01-03\n",
        )

        # Recipes CSV
        self.recipes_csv = tmp_path / "RAW_recipes.csv"
        self.recipes_csv.write_text(
            "id,name,minutes,n_steps,submitted\n"
            "101,Recipe A,30,5,2023-01-01\n"
            "102,Recipe B,120,0,2023-01-02\n"  # zéro steps
            "103,Recipe C,150,3,2023-01-03\n",
        )

        # Initialiser DataProcessor
        self.processor = DataProcessor(
            data_dir=tmp_path,
            path_interactions=self.interactions_csv,
            path_recipes=self.recipes_csv,
        )

    @pytest.fixture  # type: ignore
    def mock_recipe_analyzer(self) -> MagicMock:
        """Create a reusable mock RecipeAnalyzer instance with save method."""
        mock_analyzer = MagicMock()
        mock_analyzer.save = MagicMock()
        return mock_analyzer

    # ---------------------------
    # Tests fonctionnels de base
    # ---------------------------

    def test_load_data(self) -> None:
        """Vérifie que les CSV sont bien chargés."""
        assert isinstance(self.processor.df_interactions, pl.DataFrame)
        assert isinstance(self.processor.df_recipes, pl.DataFrame)
        assert self.processor.df_interactions.shape[0] == 3
        assert self.processor.df_recipes.shape[0] == 3

    def test_drop_na(self) -> None:
        """Vérifie la suppression des NA et des recettes irréalistes."""
        self.processor.drop_na()
        assert self.processor.df_interactions_nna.shape[0] == 2  # 1 review manquante
        assert self.processor.df_recipes_nna.shape[0] == 2  # 1 recette avec 0 steps

    def test_split_minutes(self) -> None:
        """Vérifie que les recettes sont bien bucketées en short/medium/long."""
        self.processor.drop_na()
        self.processor.split_minutes()
        assert all(self.processor.df_recipes_nna_short["minutes"] <= 100)
        assert all(
            (self.processor.df_recipes_nna_medium["minutes"] > 100)
            & (self.processor.df_recipes_nna_medium["minutes"] <= 2880),
        )

    def test_merge_data(self) -> None:
        """Vérifie le merge des interactions avec les recettes."""
        self.processor.drop_na()
        self.processor.split_minutes()
        self.processor.merge_data()

        # Vérifier merges
        assert "recipe_id" in self.processor.total.columns
        assert self.processor.total.shape[0] > 0
        assert hasattr(self.processor, "total_short")
        assert hasattr(self.processor, "total_medium")
        assert hasattr(self.processor, "total_long")

    def test_compute_proportions(self) -> None:
        """Vérifie le calcul des proportions de notes 5 étoiles."""
        self.processor.drop_na()
        self.processor.split_minutes()
        self.processor.merge_data()
        self.processor.compute_proportions()

        # Vérifier proportions
        assert "proportion_m" in self.processor.df_proportion_m.columns
        assert "proportion_s" in self.processor.df_proportion_s.columns
        assert len(self.processor.df_proportion_m) > 0
        assert len(self.processor.df_proportion_s) > 0

    @patch("mangetamain.backend.data_processor.RecipeAnalyzer")
    def test_process_recipes(
        self,
        mock_recipe_analyzer_class: MagicMock,
        mock_recipe_analyzer: MagicMock,
    ) -> None:
        """Vérifie que process_recipes crée une instance RecipeAnalyzer."""
        # Arrange: Use the fixture mock instance
        mock_recipe_analyzer_class.return_value = mock_recipe_analyzer

        self.processor.drop_na()
        self.processor.split_minutes()
        self.processor.merge_data()
        self.processor.compute_proportions()
        self.processor.process_recipes()

        assert hasattr(self.processor, "recipe_analyzer")
        assert self.processor.recipe_analyzer is not None
        assert self.processor.recipe_analyzer == mock_recipe_analyzer

    @patch("mangetamain.backend.data_processor.RecipeAnalyzer")
    @patch("builtins.open", new_callable=MagicMock)
    def test_save_data(
        self,
        mock_open_func: MagicMock,
        mock_recipe_analyzer_class: MagicMock,
        mock_recipe_analyzer: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Vérifie que save_data écrit bien les fichiers parquet."""
        # Arrange: Setup mock for RecipeAnalyzer
        mock_recipe_analyzer_class.return_value = mock_recipe_analyzer

        self.processor.drop_na()
        self.processor.split_minutes()
        self.processor.merge_data()
        self.processor.compute_proportions()
        self.processor.process_recipes()

        # Rediriger les fichiers vers tmp_path pour le test
        processed_dir = tmp_path / "processed"
        processed_dir.mkdir()

        original_write_parquet = pl.DataFrame.write_parquet

        def patched_write(
            self_df: pl.DataFrame,
            path: str | Path,
            *args: object,
            **kwargs: dict[str, object],
        ) -> None:
            path = processed_dir / Path(path).name
            original_write_parquet(self_df, path, *args, **kwargs)

        pl.DataFrame.write_parquet = patched_write
        self.processor.save_data()
        pl.DataFrame.write_parquet = original_write_parquet  # restore

        # Vérifier que certains fichiers existent
        expected_files = [
            "initial_interactions.parquet",
            "processed_interactions.parquet",
            "initial_recipes.parquet",
            "processed_recipes.parquet",
            "total.parquet",
            "short.parquet",
            "proportion_m.parquet",
            "proportion_s.parquet",
        ]
        for f in expected_files:
            assert (processed_dir / f).exists()

        # Verify that recipe_analyzer.save() was called
        mock_recipe_analyzer.save.assert_called_once()

    # ---------------------------
    # Tests d'exceptions
    # ---------------------------

    def test_missing_csv_files(self, tmp_path: Path) -> None:
        """Vérifie que FileNotFoundError est levé si CSV et ZIP manquants."""
        with pytest.raises(FileNotFoundError):
            DataProcessor(
                data_dir=tmp_path,
                path_interactions=tmp_path / "missing_interactions.csv",
                path_recipes=tmp_path / "missing_recipes.csv",
            )

    def test_corrupted_csv_file(self, tmp_path: Path) -> None:
        """Vérifie que load_data lève une exception pour un CSV interactions corrompu (mauvais format date)."""
        bad_csv = tmp_path / "bad_interactions.csv"
        bad_csv.write_text(
            "user_id,recipe_id,rating,review,date\n"
            "1,101,5,Good,notadate",  # invalid date
        )
        with pytest.raises(
            pl.exceptions.ComputeError,
            match="could not parse `notadate`",
        ):
            DataProcessor(
                data_dir=tmp_path,
                path_interactions=bad_csv,
                path_recipes=self.recipes_csv,
            )

    def test_corrupted_recipes_csv(self, tmp_path: Path) -> None:
        """Vérifie que load_data lève une exception pour un CSV recipes corrompu (mauvais format submitted)."""
        bad_csv = tmp_path / "bad_recipes.csv"
        bad_csv.write_text(
            "id,name,minutes,n_steps,submitted\n101,Recipe A,30,5,notadate",
        )
        with pytest.raises(
            pl.exceptions.ComputeError,
            match="could not parse `notadate`",
        ):
            DataProcessor(
                data_dir=tmp_path,
                path_interactions=self.interactions_csv,
                path_recipes=bad_csv,
            )

    def test_load_data_from_zip(self, tmp_path: Path) -> None:
        """Vérifie que DataProcessor extrait bien les ZIP si les CSV manquent."""
        # --- Créer les CSV valides ---
        interactions_csv = tmp_path / "RAW_interactions.csv"
        interactions_csv.write_text(
            "user_id,recipe_id,rating,review,date\n1,101,5,Great,2023-01-01\n",
        )

        recipes_csv = tmp_path / "RAW_recipes.csv"
        recipes_csv.write_text(
            "id,name,minutes,n_steps,submitted\n101,Recipe A,30,5,2023-01-01\n",
        )

        # --- Créer les ZIP contenant les CSV ---
        interactions_zip = tmp_path / "RAW_interactions.csv.zip"
        with zipfile.ZipFile(interactions_zip, "w") as zipf:
            zipf.write(interactions_csv, arcname="RAW_interactions.csv")

        recipes_zip = tmp_path / "RAW_recipes.csv.zip"
        with zipfile.ZipFile(recipes_zip, "w") as zipf:
            zipf.write(recipes_csv, arcname="RAW_recipes.csv")

        # --- Supprimer les CSV pour forcer la lecture des ZIP ---
        interactions_csv.unlink()
        recipes_csv.unlink()

        # --- Lancer le DataProcessor (doit extraire automatiquement les ZIP) ---
        processor = DataProcessor(
            data_dir=tmp_path,
            path_interactions=interactions_csv,
            path_recipes=recipes_csv,
        )

        # --- Vérifications ---
        extracted_interactions = tmp_path / "RAW_interactions.csv"
        extracted_recipes = tmp_path / "RAW_recipes.csv"

        assert extracted_interactions.exists(), (
            "Le CSV interactions devrait être extrait du ZIP"
        )
        assert extracted_recipes.exists(), "Le CSV recipes devrait être extrait du ZIP"

        # Les DataFrames doivent être chargés correctement
        assert processor.df_interactions.shape[0] == 1
        assert processor.df_recipes.shape[0] == 1

    # ---------------------------
    # Tests pour process_recipes
    # ---------------------------

    @patch("mangetamain.backend.data_processor.RecipeAnalyzer")
    def test_process_recipes_creates_analyzer(
        self,
        mock_recipe_analyzer_class: MagicMock,
        mock_recipe_analyzer: MagicMock,
    ) -> None:
        """Vérifie que process_recipes crée correctement une instance RecipeAnalyzer."""
        # Arrange: Use the fixture mock instance
        mock_recipe_analyzer_class.return_value = mock_recipe_analyzer

        # Ensure data is processed
        self.processor.drop_na()
        self.processor.split_minutes()
        self.processor.merge_data()

        # Act: Call process_recipes
        self.processor.process_recipes()

        # Assert: RecipeAnalyzer was instantiated with correct parameters
        mock_recipe_analyzer_class.assert_called_once_with(
            self.processor.df_interactions,
            self.processor.df_recipes,
            self.processor.total,
        )

        # Assert: The instance is stored in processor.recipe_analyzer
        assert self.processor.recipe_analyzer == mock_recipe_analyzer

    @patch("mangetamain.backend.data_processor.RecipeAnalyzer")
    def test_process_recipes_with_real_dataframes(
        self,
        mock_recipe_analyzer_class: MagicMock,
        mock_recipe_analyzer: MagicMock,
    ) -> None:
        """Vérifie que process_recipes passe des DataFrames Polars valides au RecipeAnalyzer."""
        # Arrange: Use the fixture mock instance
        mock_recipe_analyzer_class.return_value = mock_recipe_analyzer

        # Process data
        self.processor.drop_na()
        self.processor.split_minutes()
        self.processor.merge_data()

        # Act
        self.processor.process_recipes()

        # Assert: Check that the call was made with Polars DataFrames
        call_args = mock_recipe_analyzer_class.call_args[0]
        assert isinstance(call_args[0], pl.DataFrame), (
            "First arg should be a Polars DataFrame (df_interactions)"
        )
        assert isinstance(call_args[1], pl.DataFrame), (
            "Second arg should be a Polars DataFrame (df_recipes)"
        )
        assert isinstance(call_args[2], pl.DataFrame), (
            "Third arg should be a Polars DataFrame (total)"
        )

        # Verify the DataFrames have expected content
        assert call_args[0].shape[0] == 3, (
            "df_interactions should have 2 rows (after drop_na)"
        )
        assert call_args[1].shape[0] == 3, (
            "df_recipes should have 2 rows (after drop_na)"
        )
        assert call_args[2].shape[0] > 0, "total should have merged data"
