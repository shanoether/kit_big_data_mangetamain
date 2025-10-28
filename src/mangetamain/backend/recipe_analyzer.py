"""Recipe analysis module with NLP and visualization capabilities.

This module provides the RecipeAnalyzer class for analyzing recipe reviews and ingredients
using Natural Language Processing (NLP) techniques. It generates visualizations including
word clouds, TF-IDF analysis, Venn diagrams, and polar plots.

Key Features:
    - Batch text processing with spaCy for 5-10x performance improvement
    - LRU caching for preprocessed data and generated figures
    - Frequency-based and TF-IDF word cloud generation
    - Comparison visualizations between word extraction methods
    - Polar plots for ingredient frequency analysis
    - Integration with Streamlit for interactive UI components

Dependencies:
    - spacy: NLP processing (requires en_core_web_sm model)
    - polars: High-performance DataFrame operations
    - matplotlib: Plotting and figure generation
    - scikit-learn: TF-IDF vectorization
    - wordcloud: Word cloud generation
    - matplotlib-venn: Venn diagram visualization
    - streamlit: Web UI framework

Note:
    All visualization methods return cached matplotlib.figure.Figure objects
    to ensure instant rendering on subsequent calls.
"""

import pickle
from collections import Counter
from functools import lru_cache
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
import spacy
import inflect
import streamlit as st
from matplotlib.figure import Figure
from matplotlib_venn import venn2
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud

from mangetamain.utils.logger import get_logger

logger = get_logger()


class RecipeAnalyzer:
    """Analyzer for recipe data with NLP and visualization capabilities.

    This class provides methods to analyze recipe reviews, extract ingredients,
    generate word clouds, and create visualizations comparing different text
    analysis techniques (frequency vs TF-IDF).

    Attributes:
        df_recipe: DataFrame containing recipe information
        df_interaction: DataFrame containing user interactions and reviews
        df_total: Combined DataFrame with all data
        nlp: spaCy language model for text processing
        stop_words: Set of stop words to filter out
        top_ingredients: Pre-computed DataFrame of most common ingredients
        _cache: Dictionary storing preprocessed data and generated figures
    """

    def __init__(
        self,
        df_interactions: pl.DataFrame,
        df_recipes: pl.DataFrame,
        df_total: pl.DataFrame,
    ) -> None:
        """Initialize the RecipeAnalyzer with dataframes.

        Args:
            df_interactions: DataFrame with user reviews and ratings
            df_recipes: DataFrame with recipe details
            df_total: Combined DataFrame with all recipe and interaction data
        """
        # Store dataframes
        self.df_recipe = df_recipes
        self.df_interaction = df_interactions
        self.df_total = df_total

        # Load spaCy model (disable unused components for speed)
        self.nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])

        # Initialize stop words
        self.stop_words = set(spacy.lang.en.STOP_WORDS)
        self._extend_stop_words()

        # Pre-compute top ingredients
        self.top_ingredients = self._compute_top_ingredients()

        # Cache for preprocessed data and figures
        self._cache: dict[str, Any] = {}

        # Pre-process the most common review sets for performance
        self._preprocessed_500_best_reviews()
        self._preprocessed_500_worst_reviews()
        self._preprocessed_500_most_reviews()
        self._preprocess_word_cloud(100)
        self._preprocess_comparisons(100, 100)

    def _extend_stop_words(self) -> None:
        """Extend the default stop words with recipe-specific terms.

        Adds common recipe and review words that don't add meaningful
        information to the analysis (e.g., 'recipe', 'minute', 'good').
        """
        extra_stop_words = [
            "recipe",
            "thank",
            "instead",
            "minute",
            "hour",
            "I",
            "water",
            "bit",
            "definitely",
            "thing",
            "half",
            "way",
            "like",
            "good",
            "great",
            "make",
            "use",
            "get",
            "also",
            "just",
            "would",
            "one",
        ]
        self.stop_words.update(extra_stop_words)

    @lru_cache(maxsize=128)  # noqa: B019
    def _clean_text(self, text: str) -> list[str]:
        """Clean and tokenize a single text string.

        Uses spaCy NLP pipeline to lemmatize, filter stop words, and extract
        meaningful tokens. Results are cached for performance.

        Args:
            text: Raw text string to clean

        Returns:
            List of cleaned and lemmatized tokens

        Note:
            - Filters out verbs, stop words, and short tokens (< 3 chars)
            - Results are cached (LRU cache with max 128 entries)
            - For batch processing, use _clean_texts_batch() instead
        """
        MIN_TOKEN_LENGTH = 2
        # Return empty list for invalid input
        if not isinstance(text, str) or not text.strip():
            return []

        # Process text with spaCy
        doc = self.nlp(text.lower())

        # Extract and filter tokens
        return [
            token.lemma_
            for token in doc
            if (
                token.is_alpha  # Only alphabetic tokens
                and token.lemma_ not in self.stop_words  # Not a stop word
                and len(token.text) > MIN_TOKEN_LENGTH  # At least 3 characters
                and token.pos_ != "VERB"  # Exclude verbs
            )
        ]

    def _clean_texts_batch(self, texts: list[str]) -> list[str]:
        """Clean multiple texts in batch (5-10x faster than one-by-one).

        Uses spaCy's pipe() method to process multiple texts efficiently in batches.
        This is significantly faster than calling _clean_text() in a loop.

        Args:
            texts: List of text strings to clean

        Returns:
            Flat list of all cleaned tokens from all texts

        Note:
            Batch size is set to 50 for optimal performance.
            Use this instead of looping over _clean_text() for large datasets.
        """
        MIN_TOKEN_LENGTH = 2
        # Filter out empty/invalid texts
        valid_texts = [t.lower() for t in texts if isinstance(t, str) and t.strip()]

        if not valid_texts:
            return []

        # Process all texts in batch using spaCy's pipe (MUCH faster than loop)
        all_tokens = []
        for doc in self.nlp.pipe(valid_texts, batch_size=50):
            # Extract tokens using same filtering criteria as _clean_text
            tokens = [
                token.lemma_
                for token in doc
                if (
                    token.is_alpha
                    and token.lemma_ not in self.stop_words
                    and len(token.text) > MIN_TOKEN_LENGTH
                    and token.pos_ != "VERB"
                )
            ]
            all_tokens.extend(tokens)

        return all_tokens

    def _compute_top_ingredients(self) -> pl.DataFrame:
        """Compute the most frequently used ingredients across all recipes.

        Cleans ingredient strings, filters out common non-informative ingredients
        (salt, water, oil, etc.) and measurement units, then counts occurrences.

        Returns:
            DataFrame with columns ['ingredients', 'count'] sorted by frequency

        Note:
            Excluded ingredients are basic items that appear in almost every recipe
            and don't provide meaningful differentiation.
        """
        # Define ingredients to exclude (too common or non-specific)
        excluded = {
            "salt",
            "water",
            "oil",
            "sugar",
            "pepper",
            "butter",
            "flour",
            "olive oil",
            "vegetable oil",
            "all-purpose flour",
            "cup",
            "tablespoon",
            "salt and pepper",
            "teaspoon",
            "pound",
            "ounce",
            "gram",
            "kilogram",
            "milliliter",
            "liter",
            "black pepper",
        }
        MIN_LEN = 2

        # Initialize inflect engine for singularization
        p = inflect.engine()
        
        # Clean ingredient strings and split into individual items
        ingredients_cleaned = (
            self.df_recipe.with_columns(
                # Remove brackets and quotes from ingredient list strings
                pl.col("ingredients").str.replace_all(r"[\[\]']", "").alias("cleaned"),
            )
            .select(
                # Split by comma and explode into separate rows
                pl.col("cleaned").str.split(", ").explode().alias("ingredients"),
            )
            .filter(
                # Filter out excluded items and empty/short strings
                ~pl.col("ingredients").is_in(excluded)
                & (pl.col("ingredients") != "")
                & (pl.col("ingredients").str.len_chars() > MIN_LEN),
            )
             .with_columns(
            # Convert each ingredient to lowercase and singular form
            pl.col("ingredients")
            .str.to_lowercase()
            .map_elements(
                lambda x: p.singular_noun(x) if p.singular_noun(x) else x,
                return_dtype=pl.String,
            )
            .alias("ingredients_singular"),
             )
        )

        # Count occurrences and sort by frequency
        ingredients_counts = (
            ingredients_cleaned.group_by("ingredients")
            .agg(pl.len().alias("count"))
            .sort("count", descending=True)
        )

        return ingredients_counts

    def _preprocessed_500_most_reviews(self) -> None:
        """Pre-process ingredients from the 500 most-reviewed recipes.

        Identifies recipes with the most reviews, extracts their ingredients,
        and cleans the text for NLP analysis. Results are cached for performance.

        Note:
            Uses batch processing for efficient NLP computation.
            Results are stored in self._cache with key 'preprocessed_500_most_reviews'.
        """
        logger.info("Preprocessing 500 most reviewed recipes...")
        cache_key = "preprocessed_500_most_reviews"

        # Find the 500 recipes with most reviews
        most_reviewed_ids = (
            self.df_total.group_by("recipe_id")
            .agg(pl.len().alias("nb_reviews"))
            .sort("nb_reviews", descending=True)
            .head(500)
        )

        # Join with ingredients data - use unique() to avoid duplicates
        most_reviews_with_ing = most_reviewed_ids.join(
            self.df_total.select(["recipe_id", "ingredients"]).unique("recipe_id"),
            on="recipe_id",
            how="left",
        ).drop_nulls("ingredients")

        # Use batch processing instead of loop (MUCH faster)
        ingredients_list = most_reviews_with_ing["ingredients"].to_list()
        logger.info(f"Processing {len(ingredients_list)} ingredients strings...")
        cleaned_reviews = self._clean_texts_batch(ingredients_list)

        logger.info(f"Most reviews cleaned: {cleaned_reviews[:5]}")
        self._cache[cache_key] = cleaned_reviews

    def _preprocessed_500_best_reviews(self) -> None:
        """Preprocess review text from the 500 highest-rated recipe reviews.

        Extracts review text from the top 500 reviews sorted by rating score (5.0 being best).
        Uses batch processing with spaCy for efficient NLP computation.
        Results are stored in self._cache with key 'preprocessed_500_best_reviews'.
        """
        logger.info("Preprocessing 500 best reviews...")
        cache_key = "preprocessed_500_best_reviews"

        best_reviews = (
            self.df_interaction.sort("rating", descending=True)
            .head(500)
            .select("review")
            .to_series()
            .to_list()
        )

        # Use batch processing instead of loop (MUCH faster)
        cleaned_reviews = self._clean_texts_batch(best_reviews)
        self._cache[cache_key] = cleaned_reviews

    def _preprocessed_500_worst_reviews(self) -> None:
        """Preprocess review text from the 500 lowest-rated recipe reviews.

        Extracts review text from the bottom 500 reviews sorted by rating score (1.0 being worst).
        Uses batch processing with spaCy for efficient NLP computation.
        Results are stored in self._cache with key 'preprocessed_500_worst_reviews'.
        """
        logger.info("Preprocessing 500 worst reviews...")
        cache_key = "preprocessed_500_worst_reviews"
        # if cache_key not in self._cache:
        worst_reviews = (
            self.df_interaction.sort("rating", descending=False)
            .head(500)
            .select("review")
            .to_series()
            .to_list()
        )

        # Use batch processing instead of loop (MUCH faster)
        cleaned_reviews = self._clean_texts_batch(worst_reviews)
        logger.info(f"Worst reviews cleaned: {cleaned_reviews[:5]}")
        self._cache[cache_key] = cleaned_reviews

    def switch_filter(self, rating_filter: str) -> str:
        """Select appropriate preprocessed data cache based on rating filter.

        Args:
            rating_filter: Filter type - 'best', 'worst', or 'most' reviewed recipes.

        Returns:
            str: Cache key corresponding to the selected filter.
                 Defaults to 'preprocessed_500_best_reviews' if invalid filter provided.
        """
        if rating_filter == "best":
            cache_key = "preprocessed_500_best_reviews"
            self._cache[cache_key]
        elif rating_filter == "worst":
            cache_key = "preprocessed_500_worst_reviews"
            self._cache[cache_key]
        elif rating_filter == "most":
            cache_key = "preprocessed_500_most_reviews"
            self._cache[cache_key]
        else:
            cache_key = "preprocessed_500_best_reviews"
            self._cache[cache_key]
            logger.warning(
                f"Invalid rating_filter: {rating_filter}. Using best reviews.",
            )

        return cache_key

    def get_top_recipe_ids(
        self,
        n: int = 50,
        rating_filter: str | None = None,
    ) -> list[str]:
        """Retrieve the first n recipe IDs from the specified rating filter cache.

        Args:
            n: Number of recipe IDs to return (default: 50).
            rating_filter: Filter type - 'best', 'worst', or 'most' reviewed recipes.

        Returns:
            list[str]: List of recipe IDs, length up to n.
                       Defaults to best reviews if invalid filter provided.
        """
        cache_key = self.switch_filter(rating_filter or "best")
        recipe_ids = list(self._cache[cache_key][0:n])
        return recipe_ids

    # could use  df_total
    def get_reviews_for_recipes(self, recipe_ids: list[int]) -> list[str]:
        """Retrieve all review texts for specified recipe IDs.

        Args:
            recipe_ids: List of recipe IDs to fetch reviews for.

        Returns:
            list[str]: List of review texts matching the provided recipe IDs.
                       Results are cached for repeated queries.
        """
        cache_key = f"reviews_{recipe_ids[:3]!s}_{len(recipe_ids)}"
        if cache_key not in self._cache:
            self._cache[cache_key] = (
                self.df_interaction.filter(pl.col("recipe_id").is_in(recipe_ids))
                .select("review")
                .to_series()
                .to_list()
            )
        recipe_review = list(self._cache[cache_key])
        return recipe_review

    def plot_word_cloud(
        self,
        wordcloud_nbr_word: int,
        rating_filter: str,
        title: str,
    ) -> Figure:
        """Generate a word cloud visualization from preprocessed review text.

        Creates a word cloud showing the most frequent words in the selected review set.
        Uses frequency-based word extraction (not TF-IDF).

        Args:
            wordcloud_nbr_word: Maximum number of words to display in the cloud.
            rating_filter: Filter type - 'best', 'worst', or 'most' reviewed recipes.
            title: Title to display on the plot.

        Returns:
            matplotlib.figure.Figure: Cached figure containing the word cloud visualization.
                                      Returns figure with "No text available" if no data exists.
        """
        cache_key = f"word_cloud_{rating_filter!s}_{wordcloud_nbr_word}"
        texts = self._cache[self.switch_filter(rating_filter)]

        if cache_key not in self._cache:
            if not texts:
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.text(0.5, 0.5, "No text available", ha="center", va="center")
                ax.set_title(title)
                self._cache[cache_key] = fig
                return fig

            word_counts: Counter[str] = Counter(texts)
            word_freq = dict(word_counts.most_common(wordcloud_nbr_word))

            fig, ax = plt.subplots(figsize=(10, 5))
            wc = WordCloud(
                width=800,
                height=400,
                background_color="white",
                max_words=wordcloud_nbr_word,
                colormap="viridis",
            ).generate_from_frequencies(word_freq)

            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            ax.set_title(title)
            plt.tight_layout()
            self._cache[cache_key] = fig

        return self._cache[cache_key]

    def plot_tfidf(
        self,
        wordcloud_nbr_word: int,
        rating_filter: str,
        title: str,
    ) -> Figure:
        """Generate a word cloud visualization using TF-IDF word extraction.

        Creates a word cloud showing words with highest TF-IDF scores.
        TF-IDF identifies words that are distinctive to the selected review set
        rather than just most frequent.

        Args:
            wordcloud_nbr_word: Maximum number of words to display in the cloud.
            rating_filter: Filter type - 'best', 'worst', or 'most' reviewed recipes.
            title: Title to display on the plot.

        Returns:
            matplotlib.figure.Figure: Cached figure containing the TF-IDF word cloud.
                                      Returns figure with "No text available" if no data exists.

        Note:
            Uses preprocessed (already cleaned) tokens from cache. Does NOT re-clean text.
        """
        cache_key = f"tfidf_{rating_filter!s}_{wordcloud_nbr_word}"
        texts = self._cache[self.switch_filter(rating_filter)]

        if cache_key not in self._cache:
            # texts is already a list of cleaned tokens, just join them into documents
            # Group tokens into documents (every N tokens = 1 doc for TF-IDF)
            if not texts:
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.text(0.5, 0.5, "No text available", ha="center", va="center")
                ax.set_title(title)
                self._cache[cache_key] = fig
                return fig

            # Create documents by grouping tokens (since texts is already cleaned)
            doc_size = max(1, len(texts) // 100)  # Aim for ~100 documents
            docs = [
                " ".join(texts[i : i + doc_size])
                for i in range(0, len(texts), doc_size)
            ]

            vectorizer = TfidfVectorizer(
                max_features=wordcloud_nbr_word,
                stop_words="english",
                ngram_range=(1, 2),
            )

            vectorizer.fit_transform(docs)
            feature_names = vectorizer.get_feature_names_out()
            scores = vectorizer.idf_
            word_freq = dict(zip(feature_names, scores, strict=False))

            fig, ax = plt.subplots(figsize=(10, 5))
            wc = WordCloud(
                width=800,
                height=400,
                background_color="white",
                max_words=wordcloud_nbr_word,
                colormap="plasma",
            ).generate_from_frequencies(word_freq)

            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            ax.set_title(title)
            plt.tight_layout()
            self._cache[cache_key] = fig
        return self._cache[cache_key]

    def compare_frequency_and_tfidf(
        self,
        recipe_count: int,
        wordcloud_nbr_word: int,
        rating_filter: str,
        title: str,
    ) -> Figure:
        """Generate a Venn diagram comparing frequency-based vs TF-IDF word extraction.

        Creates a visualization showing the overlap between top words identified by
        raw frequency counting vs TF-IDF scoring. Helps identify which words are
        distinctive (TF-IDF) vs merely common (frequency).

        Args:
            recipe_count: Number of recipes to analyze (currently unused in implementation).
            wordcloud_nbr_word: Maximum features for TF-IDF vectorizer.
            rating_filter: Filter type - 'best', 'worst', or 'most' reviewed recipes.
            title: Title to display on the Venn diagram.

        Returns:
            matplotlib.figure.Figure: Cached figure containing the Venn diagram.
                                      Shows top 20 words from each method and their overlap.
        """
        cache_key = f"compare_{recipe_count}_{wordcloud_nbr_word}_{title}"
        VENN_NBR = 20

        if cache_key not in self._cache:
            cleaned = self._cache[self.switch_filter(rating_filter)]
            if not cleaned:
                fig, ax = plt.subplots(figsize=(8, 8))
                ax.text(0.5, 0.5, "No text available", ha="center", va="center")
                ax.set_title(title)
                self._cache[cache_key] = fig
                return fig

            # Raw frequency
            freq_counts: Counter[str] = Counter(cleaned)
            freq_top = {w for w, _ in freq_counts.most_common(VENN_NBR)}

            # TF-IDF
            vectorizer = TfidfVectorizer(
                max_features=wordcloud_nbr_word,
                stop_words="english",
            )
            vectorizer.fit_transform(cleaned)
            tfidf_top = set(vectorizer.get_feature_names_out()[:VENN_NBR])

            fig, ax = plt.subplots(figsize=(8, 8))
            venn2(
                [freq_top, tfidf_top],
                set_labels=("Raw Frequency", "TF-IDF"),
                set_colors=("skyblue", "salmon"),
                alpha=0.7,
                ax=ax,
            )
            ax.set_title(title)

            # Legend
            only_freq = freq_top - tfidf_top
            only_tfidf = tfidf_top - freq_top
            common = freq_top & tfidf_top

            legend_text = (
                f"Only Frequency: {len(only_freq)}\n"
                f"Only TF-IDF: {len(only_tfidf)}\n"
                f"Common: {len(common)}"
            )
            ax.text(0.5, -0.15, legend_text, ha="center", transform=ax.transAxes)

            plt.tight_layout()
            self._cache[cache_key] = fig
        return self._cache[cache_key]

    def plot_top_ingredients(self, top_n: int = 20) -> Figure:
        """Generate a polar plot showing the most common ingredients.

        Creates a radar/polar chart visualizing ingredient frequency across recipes.
        The radial distance represents the count of recipes using each ingredient.

        Args:
            top_n: Number of top ingredients to display (default: 20).

        Returns:
            matplotlib.figure.Figure: Cached polar plot figure showing ingredient distribution.
                                      Returns figure with "No ingredients found" if no data exists.
        """
        cache_key = f"top_ingredients_{top_n}"
        if cache_key not in self._cache:
            ingredients_counts = self.top_ingredients.head(top_n)

            if ingredients_counts.height == 0:
                fig, ax = plt.subplots(
                    figsize=(8, 8),
                    subplot_kw={"projection": "polar"},
                )
                ax.text(0.5, 0.5, "No ingredients found", ha="center", va="center")
                self._cache[cache_key] = fig
                return fig

            labels = ingredients_counts["ingredients"].to_list()
            values = ingredients_counts["count"].to_list()
            angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
            values += values[:1]
            angles += angles[:1]

            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"projection": "polar"})
            ax.plot(angles, values, linewidth=2, color="blue")
            ax.fill(angles, values, alpha=0.3, color="skyblue")
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(labels, rotation=45, ha="right")
            ax.set_yticklabels([])
            ax.set_title(f"Top {top_n} ingredients")
            plt.tight_layout()
            self._cache[cache_key] = fig

        return self._cache[cache_key]

    def _preprocess_word_cloud(self, wordcloud_nbr_word: int) -> None:
        categories = [
            ("Most reviewed recipes", "most"),
            ("Best rated recipes", "best"),
            ("Worst rated recipes", "worst"),
        ]
        for _i, (title, filter_type) in enumerate(categories):
            self.plot_word_cloud(
                wordcloud_nbr_word,
                filter_type,
                f"Frequency - {title}",
            )
            self.plot_tfidf(
                wordcloud_nbr_word,
                filter_type,
                f"TF-IDF - {title}",
            )

    def display_wordclouds(self, wordcloud_nbr_word: int) -> None:
        """Render a Streamlit UI with 6 word cloud visualizations.

        Creates a 2x3 grid showing frequency-based and TF-IDF word clouds for:
        - Most reviewed recipes
        - Best rated recipes
        - Worst rated recipes

        All plots are cached for instant display on subsequent renders.

        Args:
            wordcloud_nbr_word: Maximum number of words to display in each cloud.
        """
        st.subheader("🗣️ WordClouds (6 charts)")

        categories = [
            ("Most reviewed recipes", "most"),
            ("Best rated recipes", "best"),
            ("Worst rated recipes", "worst"),
        ]

        # 2x3 grid for the 6 wordclouds
        for _i, (title, filter_type) in enumerate(categories):
            st.markdown(title)
            cols = st.columns(2)

            with (
                cols[0],
                st.spinner(f"Generating WordCloud (Frequency) for {title}..."),
            ):
                fig = self.plot_word_cloud(
                    wordcloud_nbr_word,
                    filter_type,
                    f"Frequency - {title}",
                )
                st.pyplot(fig)

            with cols[1], st.spinner(f"Generating WordCloud (TF-IDF) for {title}..."):
                fig = self.plot_tfidf(
                    wordcloud_nbr_word,
                    filter_type,
                    f"TF-IDF - {title}",
                )
                st.pyplot(fig)

    def _preprocess_comparisons(
        self,
        recipe_count: int,
        wordcloud_nbr_word: int,
    ) -> None:
        """Pre-generate and cache all Venn diagram comparison figures.

        Generates comparison visualizations for all three categories (most, best,
        worst) to populate the cache. This speeds up subsequent display calls.

        Args:
            recipe_count: Number of recipes to analyze for comparisons.
            wordcloud_nbr_word: Maximum features for TF-IDF vectorization.
        """
        categories = [
            ("Most reviewed recipes", "most"),
            ("Best rated recipes", "best"),
            ("Worst rated recipes", "worst"),
        ]
        for _i, (title, filter_type) in enumerate(categories):
            self.compare_frequency_and_tfidf(
                recipe_count,
                wordcloud_nbr_word,
                filter_type,
                f"Comparison - {title}",
            )

    # Function to display comparisons
    def display_comparisons(
        self,
        recipe_count: int,
        wordcloud_nbr_word: int,
    ) -> None:
        """Render a Streamlit UI with 3 Venn diagram comparisons.

        Creates Venn diagrams comparing frequency vs TF-IDF word extraction for:
        - Most reviewed recipes
        - Best rated recipes
        - Worst rated recipes

        Shows which words are identified by both methods (common), only frequency,
        or only TF-IDF. All plots are cached for instant display.

        Args:
            recipe_count: Number of recipes to analyze (passed to comparison method).
            wordcloud_nbr_word: Maximum features for TF-IDF vectorization.
        """
        st.subheader("🔄 Frequency/TF-IDF Comparisons (3 charts)")

        categories = [
            ("Most reviewed recipes", "most"),
            ("Best rated recipes", "best"),
            ("Worst rated recipes", "worst"),
        ]

        # 1x3 grid for the 3 comparisons
        for _i, (title, filter_type) in enumerate(categories):
            with st.spinner(f"Comparison for {title}..."):
                fig = self.compare_frequency_and_tfidf(
                    recipe_count,
                    wordcloud_nbr_word,
                    filter_type,
                    f"Comparison - {title}",
                )
                st.pyplot(fig)

    def __getstate__(self) -> dict[str, Any]:
        """Prepare object for pickling - exclude spaCy model.

        The spaCy NLP model cannot be pickled directly, so we exclude it
        from the serialized state. It will be reloaded in __setstate__.

        Returns:
            dict[str, Any]: Object state dictionary without the spaCy model.
        """
        state = self.__dict__.copy()
        state["nlp"] = None  # Don't pickle the spaCy model
        return state

    def __setstate__(self, state: dict[str, Any]) -> None:
        """Restore object after unpickling - reload spaCy model.

        Args:
            state: The object state dictionary from pickle.
        """
        self.__dict__.update(state)
        # Reload the spaCy model with same configuration as __init__

        self.nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])

    def save(self, filepath: str) -> None:
        """Save the RecipeAnalyzer instance to disk using pickle.

        Args:
            filepath: Path where to save the analyzer (e.g., 'analyzer.pkl').

        Note:
            The spaCy model is excluded from serialization and reloaded on load.
        """
        with open(filepath, "wb") as f:
            pickle.dump(self, f)
        logger.info(f"RecipeAnalyzer saved to {filepath}")

    @staticmethod
    def load(filepath: str) -> "RecipeAnalyzer":
        """Load a RecipeAnalyzer instance from disk.

        Args:
            filepath: Path to the saved analyzer file.

        Returns:
            RecipeAnalyzer: Loaded analyzer instance with spaCy model reloaded.
        """
        with open(filepath, "rb") as f:
            analyzer: RecipeAnalyzer = pickle.load(f)
        logger.info(f"RecipeAnalyzer loaded from {filepath}")
        return analyzer
