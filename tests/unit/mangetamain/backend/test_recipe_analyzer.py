"""Unit tests for the RecipeAnalyzer class."""

import pickle
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import matplotlib.pyplot as plt
import polars as pl
import pytest
from matplotlib.figure import Figure

from mangetamain.backend.recipe_analyzer import RecipeAnalyzer


class TestRecipeAnalyzer:
    """Test suite for RecipeAnalyzer class."""

    @pytest.fixture(autouse=True)  # type: ignore
    def setup(self) -> None:
        """Set up test fixtures with sample data."""
        # Close all matplotlib figures before each test to avoid memory warnings
        plt.close("all")

        # Sample interactions data
        self.df_interactions = pl.DataFrame(
            {
                "user_id": [1, 2, 3, 4, 5],
                "recipe_id": [101, 102, 103, 101, 102],
                "rating": [5, 1, 5, 4, 2],
                "review": [
                    "This recipe is absolutely amazing and delicious!",
                    "Terrible recipe, very bad taste.",
                    "Great recipe, loved the flavor and ingredients.",
                    "Good recipe with nice ingredients.",
                    "Not good, disappointing results.",
                ],
                "date": ["2023-01-01"] * 5,
            },
        )

        # Sample recipes data
        self.df_recipes = pl.DataFrame(
            {
                "id": [101, 102, 103],
                "name": ["Recipe A", "Recipe B", "Recipe C"],
                "minutes": [30, 45, 60],
                "n_steps": [5, 7, 10],
                "ingredients": [
                    "['salt', 'pepper', 'garlic', 'onion']",
                    "['chicken', 'rice', 'vegetables']",
                    "['pasta', 'tomato', 'cheese', 'basil']",
                ],
                "submitted": ["2023-01-01"] * 3,
            },
        )

        # Combined data
        self.df_total = self.df_interactions.join(
            self.df_recipes,
            left_on="recipe_id",
            right_on="id",
            how="left",
        )

    @pytest.fixture  # type: ignore
    def analyzer(self) -> RecipeAnalyzer:
        """Create a RecipeAnalyzer instance for testing."""
        return RecipeAnalyzer(
            self.df_interactions,
            self.df_recipes,
            self.df_total,
        )

    # ---------------------------
    # Initialization Tests
    # ---------------------------

    def test_initialization(self, analyzer: RecipeAnalyzer) -> None:
        """Test that RecipeAnalyzer initializes correctly."""
        assert isinstance(analyzer.df_recipe, pl.DataFrame)
        assert isinstance(analyzer.df_interaction, pl.DataFrame)
        assert isinstance(analyzer.df_total, pl.DataFrame)
        assert analyzer.nlp is not None
        assert len(analyzer.stop_words) > 0
        assert isinstance(analyzer._cache, dict)

    def test_dataframes_stored(self, analyzer: RecipeAnalyzer) -> None:
        """Test that dataframes are properly stored."""
        assert analyzer.df_recipe.equals(self.df_recipes)
        assert analyzer.df_interaction.equals(self.df_interactions)
        assert analyzer.df_total.shape[0] == self.df_total.shape[0]

    def test_stop_words_extended(self, analyzer: RecipeAnalyzer) -> None:
        """Test that custom stop words are added."""
        # Check that some custom cooking-related stop words exist
        assert len(analyzer.stop_words) > 100  # Should have default + custom
        # Should contain some custom words
        custom_words = {"recipe", "make", "made", "really", "like"}
        assert any(word in analyzer.stop_words for word in custom_words)

    # ---------------------------
    # Text Cleaning Tests
    # ---------------------------

    def test_clean_text_basic(self, analyzer: RecipeAnalyzer) -> None:
        """Test basic text cleaning and lemmatization."""
        text = "The recipes are making delicious foods"
        cleaned = analyzer._clean_text(text)

        assert isinstance(cleaned, list)
        assert len(cleaned) > 0
        # Should filter out stop words and lemmatize
        assert "the" not in [word.lower() for word in cleaned]

    def test_clean_text_empty_string(self, analyzer: RecipeAnalyzer) -> None:
        """Test cleaning empty string."""
        cleaned = analyzer._clean_text("")
        assert cleaned == []

    def test_clean_texts_batch(self, analyzer: RecipeAnalyzer) -> None:
        """Test batch text cleaning."""
        texts = [
            "This is a great recipe",
            "I love cooking food",
            "Amazing delicious meal",
        ]
        cleaned = analyzer._clean_texts_batch(texts)

        assert isinstance(cleaned, list)
        # _clean_texts_batch returns a flattened list of all tokens
        assert len(cleaned) > 0
        assert all(isinstance(token, str) for token in cleaned)

    # ---------------------------
    # Filter and Data Retrieval Tests
    # ---------------------------

    def test_switch_filter_most_reviewed(self, analyzer: RecipeAnalyzer) -> None:
        """Test switch_filter returns correct cache key."""
        key = analyzer.switch_filter("most")
        assert key == "preprocessed_500_most_reviews"

    def test_switch_filter_best_reviewed(self, analyzer: RecipeAnalyzer) -> None:
        """Test switch_filter for best reviewed."""
        key = analyzer.switch_filter("best")
        assert key == "preprocessed_500_best_reviews"

    def test_switch_filter_worst_reviewed(self, analyzer: RecipeAnalyzer) -> None:
        """Test switch_filter for worst reviewed."""
        key = analyzer.switch_filter("worst")
        assert key == "preprocessed_500_worst_reviews"

    def test_get_top_recipe_ids(self, analyzer: RecipeAnalyzer) -> None:
        """Test getting top recipe IDs by filter."""
        recipe_ids = analyzer.get_top_recipe_ids(n=2, rating_filter="most")

        assert isinstance(recipe_ids, list)
        assert len(recipe_ids) <= 2
        assert all(isinstance(rid, str) for rid in recipe_ids)

    def test_get_reviews_for_recipes(self, analyzer: RecipeAnalyzer) -> None:
        """Test retrieving reviews for specific recipes."""
        recipe_ids = [101, 102]
        reviews = analyzer.get_reviews_for_recipes(recipe_ids)

        assert isinstance(reviews, list)
        assert len(reviews) > 0
        assert all(isinstance(review, str) for review in reviews)

    # ---------------------------
    # Visualization Tests
    # ---------------------------

    def test_plot_word_cloud_returns_figure(self, analyzer: RecipeAnalyzer) -> None:
        """Test that plot_word_cloud returns a matplotlib Figure."""
        fig = analyzer.plot_word_cloud(
            wordcloud_nbr_word=50,
            rating_filter="most",
            title="Test Word Cloud",
        )

        assert isinstance(fig, Figure)
        assert len(fig.axes) > 0

    def test_plot_word_cloud_caching(self, analyzer: RecipeAnalyzer) -> None:
        """Test that word cloud plots are cached."""
        # First call
        fig1 = analyzer.plot_word_cloud(
            wordcloud_nbr_word=50,
            rating_filter="most",
            title="Test",
        )

        # Second call should return cached figure
        fig2 = analyzer.plot_word_cloud(
            wordcloud_nbr_word=50,
            rating_filter="most",
            title="Test",
        )

        assert fig1 is fig2  # Same object reference = cached

    def test_plot_tfidf_returns_figure(self, analyzer: RecipeAnalyzer) -> None:
        """Test that plot_tfidf returns a matplotlib Figure."""
        fig = analyzer.plot_tfidf(
            wordcloud_nbr_word=50,
            rating_filter="most",
            title="Test TF-IDF",
        )

        assert isinstance(fig, Figure)
        assert len(fig.axes) > 0

    def test_compare_frequency_and_tfidf_returns_figure(
        self,
        analyzer: RecipeAnalyzer,
    ) -> None:
        """Test comparison visualization returns a Figure."""
        fig = analyzer.compare_frequency_and_tfidf(
            recipe_count=500,
            wordcloud_nbr_word=50,
            rating_filter="most",
            title="Comparison Test",
        )

        assert isinstance(fig, Figure)
        # Should have 3 subplots: word cloud, TF-IDF, Venn diagram
        assert len(fig.axes) >= 1  # At least 1 axis

    def test_plot_top_ingredients(self, analyzer: RecipeAnalyzer) -> None:
        """Test plotting top ingredients returns a Figure."""
        fig = analyzer.plot_top_ingredients(top_n=10)

        assert isinstance(fig, Figure)
        assert len(fig.axes) > 0

    # ---------------------------
    # Streamlit Display Tests (Mocked)
    # ---------------------------

    @patch("mangetamain.backend.recipe_analyzer.st")
    def test_display_wordclouds(
        self,
        mock_st: Mock,
        analyzer: RecipeAnalyzer,
    ) -> None:
        """Test display_wordclouds calls streamlit functions."""
        # Mock columns to return mock column objects with context manager support
        mock_col1 = Mock()
        mock_col1.__enter__ = Mock(return_value=mock_col1)
        mock_col1.__exit__ = Mock(return_value=False)

        mock_col2 = Mock()
        mock_col2.__enter__ = Mock(return_value=mock_col2)
        mock_col2.__exit__ = Mock(return_value=False)

        mock_st.columns.return_value = [mock_col1, mock_col2]

        # Mock spinner context manager
        mock_spinner = Mock()
        mock_spinner.__enter__ = Mock(return_value=mock_spinner)
        mock_spinner.__exit__ = Mock(return_value=False)
        mock_st.spinner.return_value = mock_spinner

        # Call the display method
        analyzer.display_wordclouds(wordcloud_nbr_word=50)

        # Verify streamlit.columns was called
        assert mock_st.columns.called

        # Verify pyplot was called
        assert mock_st.pyplot.called

    @patch("mangetamain.backend.recipe_analyzer.st")
    def test_display_comparisons(
        self,
        mock_st: Mock,
        analyzer: RecipeAnalyzer,
    ) -> None:
        """Test display_comparisons calls streamlit functions."""
        # Mock spinner with context manager support
        mock_spinner = Mock()
        mock_spinner.__enter__ = Mock(return_value=mock_spinner)
        mock_spinner.__exit__ = Mock(return_value=False)
        mock_st.spinner.return_value = mock_spinner

        analyzer.display_comparisons(recipe_count=500, wordcloud_nbr_word=50)

        # Verify streamlit methods were called
        assert mock_st.subheader.called
        assert mock_st.spinner.called
        assert mock_st.pyplot.called
        # Should be called 3 times (once for each category: most, best, worst)
        assert mock_st.pyplot.call_count == 3

    # ---------------------------
    # Serialization Tests
    # ---------------------------

    def test_getstate_excludes_nlp(self, analyzer: RecipeAnalyzer) -> None:
        """Test that __getstate__ excludes the spaCy model."""
        state = analyzer.__getstate__()

        # nlp should be set to None (not excluded, but nullified)
        assert state.get("nlp") is None
        assert "df_recipe" in state
        assert "df_interaction" in state
        assert "df_total" in state

    def test_setstate_reloads_nlp(self, analyzer: RecipeAnalyzer) -> None:
        """Test that __setstate__ reloads the spaCy model."""
        state = analyzer.__getstate__()

        # Create a new analyzer and restore state
        new_analyzer = RecipeAnalyzer.__new__(RecipeAnalyzer)
        new_analyzer.__setstate__(state)

        # nlp should be reloaded
        assert new_analyzer.nlp is not None
        assert hasattr(new_analyzer.nlp, "pipe")

    def test_save_and_load_pickle(self, analyzer: RecipeAnalyzer) -> None:
        """Test saving and loading RecipeAnalyzer via pickle."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".pkl") as f:
            temp_path = f.name
            analyzer.save(temp_path)

        try:
            # Load the analyzer
            loaded_analyzer = RecipeAnalyzer.load(temp_path)

            # Verify attributes are preserved
            assert isinstance(loaded_analyzer, RecipeAnalyzer)
            assert loaded_analyzer.df_recipe.equals(analyzer.df_recipe)
            assert loaded_analyzer.df_interaction.equals(analyzer.df_interaction)
            assert loaded_analyzer.nlp is not None

        finally:
            # Cleanup
            Path(temp_path).unlink(missing_ok=True)

    def test_pickle_roundtrip(self, analyzer: RecipeAnalyzer) -> None:
        """Test that RecipeAnalyzer can be pickled and unpickled."""
        # Pickle the analyzer
        pickled = pickle.dumps(analyzer)

        # Unpickle it
        loaded_analyzer = pickle.loads(pickled)

        # Verify it's properly restored
        assert isinstance(loaded_analyzer, RecipeAnalyzer)
        assert loaded_analyzer.df_recipe.equals(analyzer.df_recipe)
        assert loaded_analyzer.nlp is not None

    # ---------------------------
    # Cache Tests
    # ---------------------------

    def test_cache_initialized(self, analyzer: RecipeAnalyzer) -> None:
        """Test that cache is initialized and populated."""
        assert isinstance(analyzer._cache, dict)
        # After initialization, should have preprocessed data
        assert len(analyzer._cache) > 0

    def test_preprocessed_data_cached(self, analyzer: RecipeAnalyzer) -> None:
        """Test that preprocessed data is stored in cache."""
        # Check for expected cache keys (actual keys from implementation)
        expected_keys = [
            "preprocessed_500_most_reviews",
            "preprocessed_500_best_reviews",
            "preprocessed_500_worst_reviews",
        ]

        for key in expected_keys:
            assert key in analyzer._cache

    # ---------------------------
    # Edge Case Tests
    # ---------------------------

    def test_empty_reviews_handled(self) -> None:
        """Test handling of empty reviews."""
        df_interactions = pl.DataFrame(
            {
                "user_id": [1],
                "recipe_id": [101],
                "rating": [5],
                "review": [""],
                "date": ["2023-01-01"],
            },
        )

        df_recipes = pl.DataFrame(
            {
                "id": [101],
                "name": ["Recipe A"],
                "minutes": [30],
                "n_steps": [5],
                "ingredients": ["['salt', 'pepper']"],
                "submitted": ["2023-01-01"],
            },
        )

        df_total = df_interactions.join(
            df_recipes,
            left_on="recipe_id",
            right_on="id",
            how="left",
        )

        # Should not raise an error
        analyzer = RecipeAnalyzer(df_interactions, df_recipes, df_total)
        assert analyzer is not None

    def test_top_ingredients_computed(self, analyzer: RecipeAnalyzer) -> None:
        """Test that top ingredients are computed."""
        assert analyzer.top_ingredients is not None
        assert isinstance(analyzer.top_ingredients, pl.DataFrame)
        # Column name is "ingredients" (plural) not "ingredient"
        assert "ingredients" in analyzer.top_ingredients.columns
        assert "count" in analyzer.top_ingredients.columns

    def test_switch_filter_invalid_rating(self, analyzer: RecipeAnalyzer) -> None:
        """Test that switch_filter handles invalid rating_filter gracefully."""
        # Should log warning and return best reviews cache key
        cache_key = analyzer.switch_filter("invalid_filter")
        assert cache_key == "preprocessed_500_best_reviews"
        # Verify it's in the cache
        assert cache_key in analyzer._cache

    def test_plot_top_ingredients_empty_dataframe(self) -> None:
        """Test plot_top_ingredients with empty recipes dataframe."""
        # Create empty dataframes with explicit schema to avoid type issues
        df_interactions = pl.DataFrame(
            schema={
                "user_id": pl.Int64,
                "recipe_id": pl.Int64,
                "rating": pl.Float64,
                "review": pl.String,
                "date": pl.String,
            },
        )
        df_recipes = pl.DataFrame(
            schema={
                "id": pl.Int64,
                "name": pl.String,
                "minutes": pl.Int64,
                "n_steps": pl.Int64,
                "ingredients": pl.String,
                "submitted": pl.String,
            },
        )
        df_total = df_interactions.join(
            df_recipes,
            left_on="recipe_id",
            right_on="id",
            how="left",
        )

        analyzer = RecipeAnalyzer(df_interactions, df_recipes, df_total)

        # Should return a figure with "No ingredients found" message
        fig = analyzer.plot_top_ingredients(top_n=10)

        assert isinstance(fig, Figure)
        assert len(fig.axes) > 0

    # def test_to_singular_plural_word(self):
    #     """Test that plural words are converted to singular."""
    #     df_interactions = pl.DataFrame(
    #         schema={
    #             "user_id": pl.Int64,
    #             "recipe_id": pl.Int64,
    #             "rating": pl.Float64,
    #             "review": pl.String,
    #             "date": pl.String,
    #         },
    #     )
    #     df_recipes = pl.DataFrame(
    #         schema={
    #             "id": pl.Int64,
    #             "name": pl.String,
    #             "minutes": pl.Int64,
    #             "n_steps": pl.Int64,
    #             "ingredients": pl.String,
    #             "submitted": pl.String,
    #         },
    #     )
    #     df_total = df_interactions.join(
    #         df_recipes,
    #         left_on="recipe_id",
    #         right_on="id",
    #         how="left",
    #     )

    #     analyzer = RecipeAnalyzer(df_interactions, df_recipes, df_total)

    #     assert analyzer._to_singular("recipes") == "recipe"
    #     assert analyzer._to_singular("tomatoes") == "tomato"
    #     assert analyzer._to_singular("potatoes") == "potato"
    #     assert analyzer._to_singular("carrots") == "carrot"
    #     assert analyzer._to_singular("onions") == "onion"
    #     assert analyzer._to_singular("apples") == "apple"

    # def test_to_singular_already_singular(self):
    #     """Test that singular words remain unchanged."""
    #     df_interactions = pl.DataFrame(
    #         schema={
    #             "user_id": pl.Int64,
    #             "recipe_id": pl.Int64,
    #             "rating": pl.Float64,
    #             "review": pl.String,
    #             "date": pl.String,
    #         },
    #     )
    #     df_recipes = pl.DataFrame(
    #         schema={
    #             "id": pl.Int64,
    #             "name": pl.String,
    #             "minutes": pl.Int64,
    #             "n_steps": pl.Int64,
    #             "ingredients": pl.String,
    #             "submitted": pl.String,
    #         },
    #     )
    #     df_total = df_interactions.join(
    #         df_recipes,
    #         left_on="recipe_id",
    #         right_on="id",
    #         how="left",
    #     )

    #     analyzer = RecipeAnalyzer(df_interactions, df_recipes, df_total)

    #     assert analyzer._to_singular("recipe") == "recipe"
    #     assert analyzer._to_singular("tomato") == "tomato"
    #     assert analyzer._to_singular("potato") == "potato"
    #     assert analyzer._to_singular("carrot") == "carrot"
    #     assert analyzer._to_singular("onion") == "onion"
    #     assert analyzer._to_singular("apple") == "apple"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
