"""Recipe analysis module for text processing and visualization.

This module provides the RecipeAnalyzer class for analyzing recipe reviews,
ingredients, and generating visualizations including word clouds, TF-IDF analysis,
and Venn diagrams.
"""

import os
from typing import List, Tuple
from collections import Counter

import numpy as np
import polars as pl
import streamlit as st
import matplotlib.pyplot as plt
import spacy
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
from matplotlib_venn import venn2
from functools import lru_cache

from mangetamain.utils.logger import get_logger

logger = get_logger()

class RecipeAnalyzer:
    """Analyzer for recipe reviews and ingredients with NLP and visualization capabilities.

    This class processes recipe data, cleans review text, extracts ingredients,
    and generates various visualizations including word clouds, TF-IDF analysis,
    and comparison charts.

    Attributes:
        df_recipe (pl.DataFrame): DataFrame containing recipe information.
        df_interaction (pl.DataFrame): DataFrame containing user-recipe interactions and reviews.
        df_total (pl.DataFrame): Combined DataFrame with all recipe and review data.
        nlp (spacy.Language): spaCy language model for NLP processing.
        stop_words (set): Set of stop words to exclude from text analysis.
        top_ingredients (pl.DataFrame): Precomputed top ingredients across all recipes.
        _cache (dict): Internal cache for storing preprocessed data and plots.
    """

    def __init__(self, df_interactions, df_recipes, df_total):
        """Initialize the RecipeAnalyzer with recipe and interaction data.

        Args:
            df_interactions (pl.DataFrame): User-recipe interactions with reviews and ratings.
            df_recipes (pl.DataFrame): Recipe information including ingredients.
            df_total (pl.DataFrame): Combined dataset with all recipe and review data.
        """
        # Store dataframes
        self.df_recipe = df_recipes
        self.df_interaction = df_interactions
        self.df_total = df_total

        # Initialize NLP model (disable parser and NER for performance)
        self.nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
        self.stop_words = set(spacy.lang.en.STOP_WORDS)
        self._extend_stop_words()

        # Compute top ingredients at initialization
        self.top_ingredients = self._compute_top_ingredients()

        # Cache for storing preprocessed data and visualizations
        self._cache = {}

        # Preprocess reviews at initialization for faster access
        self._preprocessed_500_best_reviews()
        self._preprocessed_500_worst_reviews()
        self._preprocessed_500_most_reviews()


    def _extend_stop_words(self) -> None:
        """Extend the default stop words list with domain-specific words.

        Adds common recipe-related words that don't add meaningful information
        to text analysis (e.g., "recipe", "minute", "hour", generic verbs).
        This can be moved to a preprocessing step for better performance.
        """
        extra_stop_words = [
            "recipe", "thank", "instead", "minute", "hour", "I", "water", "bit",
            "definitely", "thing", "half", "way", "like", "good", "great",
            "make", "use", "get", "also", "just", "would", "one"
        ]
        self.stop_words.update(extra_stop_words)


    @lru_cache(maxsize=128)
    def _clean_text(self, text: str) -> List[str]:
        """Clean and tokenize text using spaCy NLP processing.

        Processes text by:
        - Converting to lowercase
        - Lemmatizing tokens
        - Filtering out stop words, non-alphabetic tokens, short words (<3 chars)
        - Removing verbs (focusing on nouns and adjectives)

        Uses LRU cache to avoid reprocessing the same text multiple times.

        Args:
            text (str): Raw text to clean and tokenize.

        Returns:
            List[str]: List of cleaned and lemmatized tokens.
        """
        # Return empty list for invalid input
        if not isinstance(text, str) or not text.strip():
            return []

        # Process text with spaCy
        doc = self.nlp(text.lower())

        # Filter tokens based on criteria
        return [token.lemma_ for token in doc
                if (token.is_alpha and  # Only alphabetic tokens
                token.lemma_ not in self.stop_words and  # Not a stop word
                len(token.text) > 2 and  # Longer than 2 characters
                token.pos_ != "VERB")]  # Not a verb

    def _compute_top_ingredients(self) -> pl.DataFrame:
        """Compute and rank the most frequently used ingredients across all recipes.

        Processes the ingredients column by:
        - Removing formatting characters (brackets, quotes)
        - Splitting into individual ingredients
        - Filtering out common/basic ingredients (salt, water, oil, etc.)
        - Filtering out measurement units
        - Counting occurrences and sorting by frequency

        Returns:
            pl.DataFrame: DataFrame with 'ingredients' and 'count' columns, sorted by count descending.
        """
        # Define ingredients to exclude (too common or not meaningful)
        excluded = {
            "salt", "water", "oil", "sugar", "pepper", "butter", "flour",
            "olive oil", "vegetable oil", "all-purpose flour", "cup", "tablespoon","salt and pepper",
            "teaspoon", "pound", "ounce", "gram", "kilogram", "milliliter", "liter","black pepper"
        }

        # Clean and explode ingredients column
        ingredients_cleaned = (
            self.df_recipe
            .with_columns(
                # Remove brackets and quotes from ingredients string
                pl.col("ingredients")
                .str.replace_all(r"[\[\]']", "")
                .alias("cleaned")
            )
            .select(
                # Split by comma and explode into separate rows
                pl.col("cleaned")
                .str.split(", ")
                .explode()
                .alias("ingredients")

    def _preprocessed_500_most_reviews(self) -> None:
        """Preprocess ingredients from the 500 most-reviewed recipes.

        Identifies recipes with the most reviews, retrieves their ingredients,
        cleans and tokenizes the ingredient text, and caches the result for
        later visualization and analysis.

        Stores cleaned tokens in cache with key 'preprocessed_500_most_reviews'.
        """
        logger.info("Preprocessing 500 most reviewed recipes...")
        cache_key = "preprocessed_500_most_reviews"

        # Find top 500 recipes by review count
        most_reviews = (
            self.df_total.group_by("recipe_id")
            .agg([
                pl.len().alias("nb_reviews"),
            ])
            .sort("nb_reviews", descending=True)
            .head(500)
        )

        # Join with ingredients data
        most_reviews_with_ing = (
            most_reviews.join(
                self.df_total.select(["recipe_id", "ingredients"]),
                on="recipe_id",
                how="left",
            )
        )

        # Clean and tokenize all ingredients
        cleaned_reviews = []
        for review in most_reviews_with_ing["ingredients"].to_list():
            cleaned_reviews.extend(self._clean_text(review))

        logger.info(f'Most reviews cleaned: {cleaned_reviews[:5]}')

        # Cache the cleaned tokens
        self._cache[cache_key] = cleaned_reviews
            ])
            .sort("nb_reviews", descending=True)
            .head(500)
        )
        most
    def _preprocessed_500_best_reviews(self) -> None:
        """Preprocess the 500 highest-rated reviews.

        Retrieves reviews with the highest ratings, cleans and tokenizes the text,
        and caches the result for later word cloud and TF-IDF analysis.

        Stores cleaned tokens in cache with key 'preprocessed_500_best_reviews'.
        """
        logger.info("Preprocessing 500 best reviews...")
        cache_key = "preprocessed_500_best_reviews"

        # Get top 500 reviews sorted by rating (highest first)
        best_reviews = (
            self.df_interaction
            .sort("rating", descending=True)
            .head(500)
            .select("review")
            .to_series()
            .to_list()
        )

        # Clean and tokenize all reviews
        cleaned_reviews = []
        for review in best_reviews:
            cleaned_reviews.extend(self._clean_text(review))

        # Cache the cleaned tokens
        self._cache[cache_key] = cleaned_reviews


    def _preprocessed_500_worst_reviews(self) -> None:
        """Preprocess the 500 lowest-rated reviews.

        Retrieves reviews with the lowest ratings, cleans and tokenizes the text,
        and caches the result for later word cloud and TF-IDF analysis.

        Stores cleaned tokens in cache with key 'preprocessed_500_worst_reviews'.
        """
        logger.info("Preprocessing 500 worst reviews...")
        cache_key = "preprocessed_500_worst_reviews"

        # Get bottom 500 reviews sorted by rating (lowest first)
        worst_reviews = (
            self.df_interaction
            .sort("rating", descending=False)
            .head(500)
            .select("review")
            .to_series()
            .to_list()
        )


    def switch_filter(self, rating_filter: str) -> str:
        """Get the appropriate cache key based on rating filter.

        Args:
            rating_filter (str): Filter type - "best", "worst", or "most".

        Returns:
            str: Cache key for the corresponding preprocessed review data.
        """
        if rating_filter == "best":
            cache_key = "preprocessed_500_best_reviews"
        elif rating_filter == "worst":
            cache_key = "preprocessed_500_worst_reviews"
        elif rating_filter == "most":
            cache_key = "preprocessed_500_most_reviews"
        else:
            # Default to best reviews if invalid filter provided
            cache_key = "preprocessed_500_best_reviews"
            logger.warning(f"Invalid rating_filter: {rating_filter}. Using best reviews.")

        return cache_key

    def get_top_recipe_ids(self, n: int = 50, rating_filter: str = None) -> List[str]:
        """Get top N cleaned tokens based on rating filter.

        Note: This method currently returns cleaned text tokens, not recipe IDs.
        Consider renaming or refactoring for clarity.

        Args:
            n (int): Number of tokens to return. Defaults to 50.
            rating_filter (str, optional): Filter type - "best", "worst", or "most".

        Returns:
            List[str]: List of cleaned text tokens from the specified review category.
        """
        if rating_filter == "best":
            cache_key = "preprocessed_500_best_reviews"
        elif rating_filter == "worst":
            cache_key = "preprocessed_500_worst_reviews"
        elif rating_filter == "most":
            cache_key = "preprocessed_500_most_reviews"
        else:
            cache_key = "preprocessed_500_best_reviews"
            logger.warning(f"Invalid rating_filter: {rating_filter}. Returning most reviews.")

        # Return first n tokens from cached preprocessed data
        return self._cache[cache_key][0:n]worst_reviews"
            texts = self._cache[cache_key]
        elif rating_filter == "most":
            cache_key = "preprocessed_500_most_reviews"
            texts = self._cache[cache_key]
        else:
            cache_key = "preprocessed_500_best_reviews"
            texts = self._cache[cache_key]

    def get_reviews_for_recipes(self, recipe_ids: List[str]) -> List[str]:
        """Retrieve all reviews for a given list of recipe IDs.

        Filters the interaction dataframe to get reviews for specific recipes.
        Results are cached to avoid repeated database queries.

        Args:
            recipe_ids (List[str]): List of recipe IDs to get reviews for.

        Returns:
            List[str]: List of review texts for the specified recipes.
        """
        # Create cache key based on recipe IDs
        cache_key = f"reviews_{str(recipe_ids[:3])}_{len(recipe_ids)}"

        # Check cache first
        if cache_key not in self._cache:
            # Query and cache reviews for these recipe IDs
            self._cache[cache_key] = (
                self.df_interaction
                .filter(pl.col("recipe_id").is_in(recipe_ids))
                .select("review")
                .to_series()
                .to_list()
            )
        return self._cache[cache_key]rating_filter: {rating_filter}. Returning most reviews.")

        return self._cache[cache_key][0:n]



    # could use  df_total
    def get_reviews_for_recipes(self, recipe_ids: List[str]) -> List[str]:
        cache_key = f"reviews_{str(recipe_ids[:3])}_{len(recipe_ids)}"
        if cache_key not in self._cache:
            self._cache[cache_key] = (
                self.df_interaction
                .filter(pl.col("recipe_id").is_in(recipe_ids))
                .select("review")
                .to_series()
                .to_list()
            )
        return self._cache[cache_key]


    def plot_word_cloud(self, wordcloud_nbr_word: int, rating_filter: str, title: str):
        """Generate a word cloud visualization from preprocessed reviews.

        Creates a word cloud based on word frequency from the selected review category.
        Results are cached to improve performance on repeated calls.

        Args:
            wordcloud_nbr_word (int): Maximum number of words to include in the word cloud.
            rating_filter (str): Filter type - "best", "worst", or "most".
            title (str): Title for the word cloud plot.

        Returns:
            matplotlib.figure.Figure: Word cloud visualization figure.
        """
        cache_key = f"word_cloud_{str(rating_filter)}_{wordcloud_nbr_word}"

        # Get preprocessed text based on rating filter
        if rating_filter == "best":
            texts = self._cache["preprocessed_500_best_reviews"]
        elif rating_filter == "worst":
            texts = self._cache["preprocessed_500_worst_reviews"]
        elif rating_filter == "most":
            texts = self._cache["preprocessed_500_most_reviews"]
        else:
            texts = self._cache["preprocessed_500_best_reviews"]
            logger.warning(f"Invalid rating_filter: {rating_filter}. Using best reviews.")

        # Check cache before generating
        if cache_key not in self._cache:
            # Handle empty text case
            if not texts:
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.text(0.5, 0.5, "No text available", ha='center', va='center')
                ax.set_title(title)
                self._cache[cache_key] = fig
                return fig

            # Count word frequencies
            word_counts = Counter(texts)
            word_freq = dict(word_counts.most_common(wordcloud_nbr_word))

            # Generate word cloud
            fig, ax = plt.subplots(figsize=(10, 5))
            wc = WordCloud(
                width=800,
                height=400,
                background_color='white',
                max_words=wordcloud_nbr_word,
                colormap="viridis"
            ).generate_from_frequencies(word_freq)

            # Display word cloud
            ax.imshow(wc, interpolation='bilinear')
            ax.axis('off')
            ax.set_title(title)
            plt.tight_layout()

            # Cache the figure
            self._cache[cache_key] = fig

        return self._cache[cache_key]

    def plot_tfidf(self, wordcloud_nbr_word: int, rating_filter: str, title: str):
        """Generate a TF-IDF based word cloud visualization.

        Creates a word cloud based on TF-IDF scores rather than raw frequency,
        highlighting words that are distinctive to the selected review category.
        Uses bigrams (1-2 word phrases) for richer context.

        Args:
            wordcloud_nbr_word (int): Maximum number of features/words to extract.
            rating_filter (str): Filter type - "best", "worst", or "most".
            title (str): Title for the word cloud plot.

        Returns:
            matplotlib.figure.Figure: TF-IDF word cloud visualization figure.
        """
        cache_key = f"tfidf_{str(rating_filter)}_{wordcloud_nbr_word}"

        # Get preprocessed text based on rating filter
        if rating_filter == "best":
            texts = self._cache["preprocessed_500_best_reviews"]
        elif rating_filter == "worst":
            texts = self._cache["preprocessed_500_worst_reviews"]
        elif rating_filter == "most":
            texts = self._cache["preprocessed_500_most_reviews"]
        else:
            texts = self._cache["preprocessed_500_best_reviews"]
            logger.warning(f"Invalid rating_filter: {rating_filter}. Using best reviews.")

        # Check cache before generating
        if cache_key not in self._cache:
            # Reconstruct documents from cleaned tokens for TF-IDF
            docs = [" ".join(self._clean_text(text)) for text in texts if text]

            # Handle empty documents case
            if not docs:
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.text(0.5, 0.5, "No text available", ha='center', va='center')
                ax.set_title(title)
                self._cache[cache_key] = fig
                return fig

            # Compute TF-IDF scores with bigrams
            vectorizer = TfidfVectorizer(
                max_features=wordcloud_nbr_word,
                stop_words='english',
                ngram_range=(1, 2)  # Include unigrams and bigrams
            )

            tfidf = vectorizer.fit_transform(docs)


    def compare_frequency_and_tfidf(self, recipe_count: int, wordcloud_nbr_word: int,
                                    rating_filter: str, title: str):
        """Generate a Venn diagram comparing frequency-based and TF-IDF word extraction.

        Creates a Venn diagram showing overlap between top words identified by
        raw frequency vs. TF-IDF scoring. This highlights which words are common
        (high frequency) vs. distinctive (high TF-IDF).

        Args:
            recipe_count (int): Number of recipes to analyze (currently unused).
            wordcloud_nbr_word (int): Maximum features for TF-IDF extraction.
            rating_filter (str): Filter type - "best", "worst", or "most".
            title (str): Title for the Venn diagram.

        Returns:
            matplotlib.figure.Figure: Venn diagram comparing the two methods.
        """
        cache_key = f"compare_{recipe_count}_{wordcloud_nbr_word}_{title}"
        VENN_NBR = 20  # Number of top words to compare in Venn diagram

        # Check cache first
        if cache_key not in self._cache:
            # Get preprocessed cleaned tokens
            cleaned = self._cache[self.switch_filter(rating_filter)]

            # Handle empty data case
            if not cleaned:
                fig, ax = plt.subplots(figsize=(8, 8))
                ax.text(0.5, 0.5, "No text available", ha='center', va='center')
                ax.set_title(title)
                self._cache[cache_key] = fig
                return fig

            # Method 1: Raw frequency counts
            freq_counts = Counter(cleaned)
            freq_top = set([w for w, _ in freq_counts.most_common(VENN_NBR)])

            # Method 2: TF-IDF scoring
            vectorizer = TfidfVectorizer(
                max_features=wordcloud_nbr_word,
                stop_words='english'
            )
            tfidf = vectorizer.fit_transform(cleaned)
            scores = tfidf.sum(axis=0).A1
            tfidf_top = set(vectorizer.get_feature_names_out()[:VENN_NBR])

            # Create Venn diagram
            fig, ax = plt.subplots(figsize=(8, 8))
            venn2(
                [freq_top, tfidf_top],
                set_labels=("Raw Frequency", "TF-IDF"),
                set_colors=("skyblue", "salmon"),
                alpha=0.7,
                ax=ax
            )
            ax.set_title(title)

            # Calculate set differences for legend
            only_freq = freq_top - tfidf_top
            only_tfidf = tfidf_top - freq_top
            common = freq_top & tfidf_top

            # Add legend with counts
            legend_text = (
                f"Only Frequency: {len(only_freq)}\n"
                f"Only TF-IDF: {len(only_tfidf)}\n"
                f"Common: {len(common)}"
            )
            ax.text(0.5, -0.15, legend_text, ha='center', transform=ax.transAxes)

            plt.tight_layout()

            # Cache the figure
            self._cache[cache_key] = fig

        return self._cache[cache_key]r.get_feature_names_out()[:VENN_NBR])

            fig, ax = plt.subplots(figsize=(8, 8))


    def plot_top_ingredients(self, top_n: int = 20):
        """Generate a radar/polar chart of the most common ingredients.

        Creates a circular radar chart showing the frequency of the top N ingredients
        across all recipes. Cached for performance on repeated calls.

        Args:
            top_n (int): Number of top ingredients to display. Defaults to 20.

        Returns:
            matplotlib.figure.Figure: Radar chart visualization of top ingredients.
        """
        cache_key = f"top_ingredients_{top_n}"

        # Check cache first
        if cache_key not in self._cache:
            # Get top N ingredients from precomputed data
            ingredients_counts = self.top_ingredients.head(top_n)

        # Handle empty data case
        if ingredients_counts.height == 0:
            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})
            ax.text(0.5, 0.5, "No ingredients found", ha='center', va='center')
            self._cache[cache_key] = fig
            return fig

        # Extract labels and values for radar chart
        labels = ingredients_counts["ingredients"].to_list()
        values = ingredients_counts["count"].to_list()

        # Calculate angles for each ingredient on the circle
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()

        # Close the plot by repeating the first value
        values += values[:1]
        angles += angles[:1]

        # Create radar chart
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})
        ax.plot(angles, values, linewidth=2, color="blue")
        ax.fill(angles, values, alpha=0.3, color="skyblue")

        # Set ingredient labels at each angle
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.set_yticklabels([])  # Hide radial labels
        ax.set_title(f"Top {top_n} Ingredients")
        plt.tight_layout()

        # Cache the figure
        self._cache[cache_key] = fig

        return self._cache[cache_key]he:
            ingredients_counts = self.top_ingredients.head(top_n)

        if ingredients_counts.height == 0:
            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})
            ax.text(0.5, 0.5, "Aucun ingrédient trouvé", ha='center', va='center')
            self._cache[cache_key] = fig
            return fig

        labels = ingredients_counts["ingredients"].to_list()
        values = ingredients_counts["count"].to_list()
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})
        ax.plot(angles, values, linewidth=2, color="blue")
        ax.fill(angles, values, alpha=0.3, color="skyblue")
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.set_yticklabels([])
        ax.set_title(f"Top {top_n} ingrédients")
        plt.tight_layout()
        self._cache[cache_key] = fig

        return self._cache[cache_key]


    def display_wordclouds(self, wordcloud_nbr_word: int):
        """Display a 2x3 grid of word clouds in Streamlit.

        Generates 6 word clouds (2 per category: frequency-based and TF-IDF-based)
        for most reviewed, best rated, and worst rated recipes.

        Args:
            wordcloud_nbr_word (int): Maximum number of words in each word cloud.
        """
        st.header("🗣️ WordClouds (6 charts)")

        # Define categories to analyze
        categories = [
            ("Most Reviewed Recipes", "most"),
            ("Best Rated Recipes", "best"),
            ("Worst Rated Recipes", "worst")
        ]

        # Create 2x3 grid: 2 columns per category
        for i, (title, filter_type) in enumerate(categories):
            st.subheader(title)
            cols = st.columns(2)

            # Left column: Frequency-based word cloud
            with cols[0]:
                with st.spinner(f"Generating Word Cloud (Frequency) for {title}..."):
                    fig = self.plot_word_cloud(
                        wordcloud_nbr_word,
                        filter_type,
                        f"Frequency - {title}",
                    )
                    st.pyplot(fig)

            # Right column: TF-IDF-based word cloud
            with cols[1]:
                with st.spinner(f"Generating Word Cloud (TF-IDF) for {title}..."):
                    fig = self.plot_tfidf(
                        wordcloud_nbr_word,
                        filter_type,
                        f"TF-IDF - {title}"
                    )
                    st.pyplot(fig)


    def display_comparisons(self, recipe_count: int, wordcloud_nbr_word: int):
        """Display a 3x1 grid of Venn diagrams comparing frequency and TF-IDF.

        Generates 3 Venn diagrams (one per category) comparing the top words
        identified by raw frequency vs. TF-IDF scoring.

        Args:
            recipe_count (int): Number of recipes to analyze.
            wordcloud_nbr_word (int): Maximum features for TF-IDF extraction.
        """
        st.header("🔄 Frequency/TF-IDF Comparisons (3 charts)")

        # Define categories to analyze
        categories = [
            ("Most Reviewed Recipes", "most"),
            ("Best Rated Recipes", "best"),
            ("Worst Rated Recipes", "worst")
        ]

        # Create 3x1 grid for Venn diagrams
        rows = st.rows(3)
        for i, (title, filter_type) in enumerate(categories):
            with rows[i]:
                with st.spinner(f"Comparison for {title}..."):
                    fig = self.compare_frequency_and_tfidf(
                        recipe_count, wordcloud_nbr_word,
                        filter_type, f"Comparison - {title}"
                    )
                    st.pyplot(fig)



    # Fonction pour afficher les comparaisons avec sabliers
    def display_comparisons(self,recipe_count, wordcloud_nbr_word):
        st.header("🔄 Comparaisons Fréquence/TF-IDF (3 graphiques)")

        categories = [
            ("Recettes les plus commentées", "most"),
            ("Recettes mieux notées", "best"),
            ("Recettes moins bien notées", "worst")
        ]

        # Grille 1x3 pour les 3 comparaisons
        rows = st.rows(3)
        for i, (title, filter_type) in enumerate(categories):
            with rows[i]:
                with st.spinner(f"Comparaison pour {title}..."):
                    # recipe_ids = self.get_top_recipe_ids(
                    #     n=recipe_count,
                    #     rating_filter=filter_type
                    # )
                    # reviews = self.get_reviews_for_recipes(recipe_ids)
                    fig = self.compare_frequency_and_tfidf(
                        recipe_count, wordcloud_nbr_word,
                        filter_type, f"Comparaison - {title}"
                    )
                    st.pyplot(fig)
