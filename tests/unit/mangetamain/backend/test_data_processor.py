# test_dataprocessor.py
import pytest
import polars as pl
from mangetamain.backend.data_processor import DataProcessor


class TestDataProcessor:
    """Tests pour le module DataProcessor."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Créer des fichiers CSV temporaires et initialiser DataProcessor."""
        # Interactions CSV
        self.interactions_csv = tmp_path / "RAW_interactions.csv"
        self.interactions_csv.write_text(
            "user_id,recipe_id,rating,review,date\n"
            "1,101,5,Great,2023-01-01\n"
            "2,102,4,,2023-01-02\n"  # NA review
            "3,103,5,Excellent,2023-01-03\n"
        )

        # Recipes CSV
        self.recipes_csv = tmp_path / "RAW_recipes.csv"
        self.recipes_csv.write_text(
            "id,name,minutes,n_steps,submitted\n"
            "101,Recipe A,30,5,2023-01-01\n"
            "102,Recipe B,120,0,2023-01-02\n"  # zéro steps
            "103,Recipe C,150,3,2023-01-03\n"
        )

        # Initialiser DataProcessor
        self.processor = DataProcessor(
            data_dir=tmp_path,
            path_interactions=self.interactions_csv,
            path_recipes=self.recipes_csv,
        )

    def test_load_data(self):
        """Vérifie que les CSV sont bien chargés."""
        assert isinstance(self.processor.df_interactions, pl.DataFrame)
        assert isinstance(self.processor.df_recipes, pl.DataFrame)
        assert self.processor.df_interactions.shape[0] == 3
        assert self.processor.df_recipes.shape[0] == 3

    def test_drop_na(self):
        """Vérifie la suppression des NA et des recettes irréalistes."""
        self.processor.drop_na()
        assert self.processor.df_interactions_nna.shape[0] == 2  # 1 review manquante
        assert self.processor.df_recipes_nna.shape[0] == 2       # 1 recette avec 0 steps

    def test_split_minutes(self):
        """Vérifie que les recettes sont bien bucketées en short/medium/long."""
        self.processor.drop_na()
        self.processor.split_minutes()
        assert all(self.processor.df_recipes_nna_short["minutes"] <= 100)
        assert all(
            (self.processor.df_recipes_nna_medium["minutes"] > 100) &
            (self.processor.df_recipes_nna_medium["minutes"] <= 2880)
        )

    def test_merge_and_compute(self):
        """Vérifie le merge et le calcul des proportions."""
        self.processor.drop_na()
        self.processor.split_minutes()
        self.processor.merge_data()
        self.processor.compute_proportions()

        # Vérifier merges
        assert "recipe_id" in self.processor.total.columns
        assert self.processor.total.shape[0] > 0

        # Vérifier proportions
        assert "proportion_m" in self.processor.df_proportion_m.columns
        assert "proportion_s" in self.processor.df_proportion_s.columns
