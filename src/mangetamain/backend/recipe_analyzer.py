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
    def __init__(self, df_interactions, df_recipes, df_total):
        self.df_recipe = df_recipes
        self.df_interaction = df_interactions
        self.df_total = df_total
        self.nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
        self.stop_words = set(spacy.lang.en.STOP_WORDS)
        self._extend_stop_words()
        #self.clean_text = self._clean_text()
        self.top_ingredients = self._compute_top_ingredients()
        # Cache des données pré-traitées
        self._cache = {}
        self._preprocessed_500_best_reviews()
        self._preprocessed_500_worst_reviews()       
        self._preprocessed_500_most_reviews()

        
    # can be done in preprocessing step
    def _extend_stop_words(self) -> None:
        extra_stop_words = [
            "recipe", "thank", "instead", "minute", "hour", "I", "water", "bit",
            "definitely", "thing", "half", "way", "like", "good", "great",
            "make", "use", "get", "also", "just", "would", "one"
        ]
        self.stop_words.update(extra_stop_words)
        

    @lru_cache(maxsize=128)
    def _clean_text(self, text: str) -> List[str]:
        if not isinstance(text, str) or not text.strip():
            return []
        doc = self.nlp(text.lower())
        return [token.lemma_ for token in doc
                if (token.is_alpha and
                token.lemma_ not in self.stop_words and
                len(token.text) > 2 and
                token.pos_ != "VERB")]

    def _compute_top_ingredients(self) -> pl.DataFrame:
        excluded = {
            "salt", "water", "oil", "sugar", "pepper", "butter", "flour",
            "olive oil", "vegetable oil", "all-purpose flour", "cup", "tablespoon","salt and pepper",
            "teaspoon", "pound", "ounce", "gram", "kilogram", "milliliter", "liter","black pepper"
        }

        ingredients_cleaned = (
            self.df_recipe
            .with_columns(
                pl.col("ingredients")
                .str.replace_all(r"[\[\]']", "")
                .alias("cleaned")
            )
            .select(
                pl.col("cleaned")
                .str.split(", ")
                .explode()
                .alias("ingredients")
            )
            .filter(
                ~pl.col("ingredients").is_in(excluded) &
                (pl.col("ingredients") != "") &
                (pl.col("ingredients").str.len_chars() > 2)
            )
        )

        ingredients_counts = (
            ingredients_cleaned
            .group_by("ingredients")
            .agg(pl.len().alias("count"))
            .sort("count", descending=True)
        )

        return ingredients_counts

    def _preprocessed_500_most_reviews(self) -> None:
        logger.info("Preprocessing 500 most reviewed recipes...")
        cache_key = "preprocessed_500_most_reviews"
        #if cache_key not in self._cache:
        most_reviews = (
            self.df_total.group_by("recipe_id")
            .agg([
                pl.len().alias("nb_reviews"),
            ])
            .sort("nb_reviews", descending=True)
            .head(500)
        )
        most_reviews_with_ing = (
            most_reviews.join(
                self.df_total.select(["recipe_id", "ingredients"]),
                on="recipe_id",
                how="left",
            )
        )
        cleaned_reviews = []
        for review in most_reviews_with_ing["ingredients"].to_list():
            cleaned_reviews.extend(self._clean_text(review))

        logger.info(f'Most reviews cleaned: {cleaned_reviews[:5]}')
        
        self._cache[cache_key] = cleaned_reviews
            
    def _preprocessed_500_best_reviews(self) -> None:
        logger.info("Preprocessing 500 best reviews...")
        cache_key = "preprocessed_500_best_reviews"
        #if cache_key not in self._cache:
        best_reviews = (
            self.df_interaction
            .sort("rating", descending=True)
            .head(500)
            .select("review")
            .to_series()
            .to_list()
        )
        cleaned_reviews = []
        for review in best_reviews:
            cleaned_reviews.extend(self._clean_text(review))
            
        self._cache[cache_key] = cleaned_reviews


    def _preprocessed_500_worst_reviews(self) -> None:
        logger.info("Preprocessing 500 worst reviews...")
        cache_key = "preprocessed_500_worst_reviews"
        #if cache_key not in self._cache:
        worst_reviews = (
            self.df_interaction
            .sort("rating", descending=False)
            .head(500)
            .select("review")
            .to_series()
            .to_list()
        )
        cleaned_reviews = []
        for review in worst_reviews:
            cleaned_reviews.extend(self._clean_text(review))
        logger.info(f'Worst reviews cleaned: {cleaned_reviews[:5]}')
        self._cache[cache_key] = cleaned_reviews
        
        
    def switch_filter(self,rating_filter):
        if rating_filter == "best":
            cache_key = "preprocessed_500_best_reviews" 
            texts = self._cache[cache_key]
        elif rating_filter == "worst":  
            cache_key = "preprocessed_500_worst_reviews"
            texts = self._cache[cache_key]
        elif rating_filter == "most":
            cache_key = "preprocessed_500_most_reviews"
            texts = self._cache[cache_key]
        else:
            cache_key = "preprocessed_500_best_reviews"
            texts = self._cache[cache_key]
            logger.warning(f"Invalid rating_filter: {rating_filter}. Using best reviews.")
            
        return cache_key

    def get_top_recipe_ids(self, n: int = 50, rating_filter: str = None) -> List[str]:
        
        if rating_filter == "best":
            cache_key = f"preprocessed_500_best_reviews"     
        elif rating_filter == "worst":
            cache_key = f"preprocessed_500_worst_reviews"
        elif rating_filter == "most":
            cache_key = f"preprocessed_500_most_reviews"
        else:
            cache_key = f"preprocessed_500_best_reviews"     
            logger.warning(f"Invalid rating_filter: {rating_filter}. Returning most reviews.")

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
        cache_key = f"word_cloud_{str(rating_filter)}_{wordcloud_nbr_word}"
        if rating_filter == "best":
            texts = self._cache["preprocessed_500_best_reviews"]
        elif rating_filter == "worst":  
            texts = self._cache["preprocessed_500_worst_reviews"]
        elif rating_filter == "most":
            texts = self._cache["preprocessed_500_most_reviews"]
        else:
            texts = self._cache["preprocessed_500_best_reviews"]
            logger.warning(f"Invalid rating_filter: {rating_filter}. Using best reviews.")
            
        if cache_key not in self._cache:
            if not texts:
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.text(0.5, 0.5, "Aucun texte disponible", ha='center', va='center')
                ax.set_title(title)
                self._cache[cache_key] = fig
                return fig

            word_counts = Counter(texts)
            word_freq = dict(word_counts.most_common(wordcloud_nbr_word))

            fig, ax = plt.subplots(figsize=(10, 5))
            wc = WordCloud(
                width=800,
                height=400,
                background_color='white',
                max_words=wordcloud_nbr_word,
                colormap="viridis"
            ).generate_from_frequencies(word_freq)

            ax.imshow(wc, interpolation='bilinear')
            ax.axis('off')
            ax.set_title(title)
            plt.tight_layout()
            self._cache[cache_key] = fig
            
        return self._cache[cache_key]

    def plot_tfidf(self, wordcloud_nbr_word: int, rating_filter: str, title: str):
        cache_key = f"tfidf_{str(rating_filter)}_{wordcloud_nbr_word}"

        if rating_filter == "best":
            texts = self._cache["preprocessed_500_best_reviews"]
        elif rating_filter == "worst":  
            texts = self._cache["preprocessed_500_worst_reviews"]
        elif rating_filter == "most":
            texts = self._cache["preprocessed_500_most_reviews"]
        else:
            texts = self._cache["preprocessed_500_best_reviews"]
            logger.warning(f"Invalid rating_filter: {rating_filter}. Using best reviews.")
            
            
        if cache_key not in self._cache:
            docs = [" ".join(self._clean_text(text)) for text in texts if text]
            if not docs:
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.text(0.5, 0.5, "Aucun texte disponible", ha='center', va='center')
                ax.set_title(title)
                self._cache[cache_key] = fig
                return fig

            vectorizer = TfidfVectorizer(
                max_features=wordcloud_nbr_word,
                stop_words='english',
                ngram_range=(1, 2)
            )

            tfidf = vectorizer.fit_transform(docs)
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf.sum(axis=0).A1
            word_freq = dict(zip(feature_names, scores))

            fig, ax = plt.subplots(figsize=(10, 5))
            wc = WordCloud(
                width=800,
                height=400,
                background_color='white',
                max_words=wordcloud_nbr_word,
                colormap="plasma"
            ).generate_from_frequencies(word_freq)

            ax.imshow(wc, interpolation='bilinear')
            ax.axis('off')
            ax.set_title(title)
            plt.tight_layout()
            self._cache[cache_key] = fig
        return self._cache[cache_key]


    def compare_frequency_and_tfidf(self, recipe_count, wordcloud_nbr_word, rating_filter, title: str):
        cache_key = f"compare_{recipe_count}_{wordcloud_nbr_word}_{title}"
        VENN_NBR = 20
        
        if cache_key not in self._cache:
            cleaned = self._cache[self.switch_filter(rating_filter)]
            if not cleaned:
                fig, ax = plt.subplots(figsize=(8, 8))
                ax.text(0.5, 0.5, "Aucun texte disponible", ha='center', va='center')
                ax.set_title(title)
                self._cache[cache_key] = fig
                return fig

            # Fréquence brute
            freq_counts = Counter(cleaned)
            freq_top = set([w for w, _ in freq_counts.most_common(VENN_NBR)])

            # TF-IDF
            vectorizer = TfidfVectorizer(
                max_features=wordcloud_nbr_word,
                stop_words='english'
            )
            tfidf = vectorizer.fit_transform(cleaned)
            scores = tfidf.sum(axis=0).A1
            tfidf_top = set(vectorizer.get_feature_names_out()[:VENN_NBR])

            fig, ax = plt.subplots(figsize=(8, 8))
            venn2(
                [freq_top, tfidf_top],
                set_labels=("Fréquence brute", "TF-IDF"),
                set_colors=("skyblue", "salmon"),
                alpha=0.7,
                ax=ax
            )
            ax.set_title(title)

            # Légende
            only_freq = freq_top - tfidf_top
            only_tfidf = tfidf_top - freq_top
            common = freq_top & tfidf_top

            legend_text = (
                f"Uniquement Fréquence: {len(only_freq)}\n"
                f"Uniquement TF-IDF: {len(only_tfidf)}\n"
                f"Communs: {len(common)}"
            )
            ax.text(0.5, -0.15, legend_text, ha='center', transform=ax.transAxes)

            plt.tight_layout()
            self._cache[cache_key] = fig
        return self._cache[cache_key]



    def plot_top_ingredients(self, top_n: int = 20):
        cache_key = f"top_ingredients_{top_n}"
        if cache_key not in self._cache:
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
        st.header("🗣️ WordClouds (6 graphiques)")

        categories = [
            ("Recettes les plus commentées", "most"),
            ("Recettes mieux notées", "best"),
            ("Recettes moins bien notées", "worst")
        ]

        # Grille 2x3 pour les 6 wordclouds
        for i, (title, filter_type) in enumerate(categories):
            st.subheader(title)
            cols = st.columns(2)

            with cols[0]:
                with st.spinner(f"Génération WordCloud (Fréquence) pour {title}..."):
                    # recipe_ids = recipe_analyzer.get_top_recipe_ids(
                    #     n=review_count,
                    #     rating_filter=filter_type
                    # )
                    # reviews = recipe_analyzer.get_reviews_for_recipes(recipe_ids)
                    fig = self.plot_word_cloud(
                        wordcloud_nbr_word,
                        filter_type,
                        f"Fréquence - {title}",
                    )
                    st.pyplot(fig)

            with cols[1]:
                with st.spinner(f"Génération WordCloud (TF-IDF) pour {title}..."):
                    fig = self.plot_tfidf(
                        wordcloud_nbr_word,
                        filter_type,
                        f"TF-IDF - {title}"
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