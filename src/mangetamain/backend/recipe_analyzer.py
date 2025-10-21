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
    def __init__(self, df_interactions, df_recipes):
        self.df_recipe = df_recipes
        self.df_interaction = df_interactions
        self.nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
        self.stop_words = set(spacy.lang.en.STOP_WORDS)
        self._extend_stop_words()
        self.clean_text = self._clean_text()
        # Cache des données pré-traitées
        self._cache = {}

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


    def _preprocessed_500_best_reviews(self) -> None:
        cache_key = "preprocessed_500_best_reviews"
        if cache_key not in self._cache:
            best_reviews = (
                self.df_interaction
                .sort("rating", descending=True)
                .head(500)
                .to_series()
                .to_list()
            )
            cleaned_reviews = []
            for review in best_reviews:
                cleaned_reviews.extend(self._clean_text(review))
                
            self._cache[cache_key] = cleaned_reviews


    def _preprocessed_500_worst_reviews(self) -> None:
        cache_key = "preprocessed_500_worst_reviews"
        if cache_key not in self._cache:
            worst_reviews = (
                self.df_interaction
                .sort("rating", ascending=True)
                .head(500)
                .to_series()
                .to_list()
            )
            cleaned_reviews = []
            for review in worst_reviews:
                cleaned_reviews.extend(self._clean_text(review))
                
            self._cache[cache_key] = cleaned_reviews


    # def _preprocess_reviews(self, texts: List[str]) -> List[str]:
    #     cache_key = str(texts[:5]) + str(len(texts))  # Clé de cache simple
    #     if cache_key not in self._cache:
    #         cleaned_texts = []
    #         for text in texts:
    #             cleaned_texts.extend(self.clean_text)
    #         self._cache[cache_key] = cleaned_texts
    #     return self._cache[cache_key]
    

    def get_top_recipe_ids(self, n: int = 50, rating_filter: str = None) -> List[str]:
        
        if rating_filter == "best":
            cache_key = f"preprocessed_500_best_reviews"     
            self._preprocessed_500_best_reviews()
        elif rating_filter == "worst":
            cache_key = f"preprocessed_500_worst_reviews"
        else:
            cache_key = f"preprocessed_500_best_reviews" 
            logger.warning(f"Invalid rating_filter: {rating_filter}. Returning best reviews.")
        
        return self._cache[cache_key][0:n]
        
        # if cache_key not in self._cache:
        #     df = (self.df_interaction
        #           .group_by("recipe_id")
        #           .agg([
        #               pl.count().alias("comment_count"),
        #               pl.col("rating").mean().alias("avg_rating")
        #           ])
        #           .filter(pl.col("comment_count") >= 10))  # Filtre 10 commentaires minimum

        #     if rating_filter == "best":
        #         df = df.filter(pl.col("avg_rating") == 5)
        #     elif rating_filter == "worst":
        #         df = df.filter(pl.col("avg_rating") == 0)

        #     self._cache[cache_key] = df.sort("comment_count", descending=True).head(n)["recipe_id"].to_list()
        return self._cache[cache_key]
    

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


    def plot_word_frequency(self, texts: List[str], title: str, max_features: int):
        cache_key = f"word_freq_{str(texts[:3])}_{len(texts)}_{max_features}"
        if cache_key not in self._cache:
            cleaned = self._preprocess_reviews(texts)
            if not cleaned:
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.text(0.5, 0.5, "Aucun texte disponible", ha='center', va='center')
                ax.set_title(title)
                self._cache[cache_key] = fig
                return fig

            word_counts = Counter(cleaned)
            word_freq = dict(word_counts.most_common(max_features))

            fig, ax = plt.subplots(figsize=(10, 5))
            wc = WordCloud(
                width=800,
                height=400,
                background_color='white',
                max_words=max_features,
                colormap="viridis"
            ).generate_from_frequencies(word_freq)

            ax.imshow(wc, interpolation='bilinear')
            ax.axis('off')
            ax.set_title(title)
            plt.tight_layout()
            self._cache[cache_key] = fig
        return self._cache[cache_key]

    def plot_tfidf(self, texts: List[str], title: str, max_features: int):
        cache_key = f"tfidf_{str(texts[:3])}_{len(texts)}_{max_features}"
        if cache_key not in self._cache:
            docs = [" ".join(self._clean_text(text)) for text in texts if text]
            if not docs:
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.text(0.5, 0.5, "Aucun texte disponible", ha='center', va='center')
                ax.set_title(title)
                self._cache[cache_key] = fig
                return fig

            vectorizer = TfidfVectorizer(
                max_features=max_features,
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
                max_words=max_features,
                colormap="plasma"
            ).generate_from_frequencies(word_freq)

            ax.imshow(wc, interpolation='bilinear')
            ax.axis('off')
            ax.set_title(title)
            plt.tight_layout()
            self._cache[cache_key] = fig
        return self._cache[cache_key]

    def compare_frequency_and_tfidf(self, texts: List[str], title: str, max_features: int):
        cache_key = f"compare_{str(texts[:3])}_{len(texts)}_{max_features}"
        if cache_key not in self._cache:
            cleaned = [" ".join(self._clean_text(t)) for t in texts if t]
            if not cleaned:
                fig, ax = plt.subplots(figsize=(8, 8))
                ax.text(0.5, 0.5, "Aucun texte disponible", ha='center', va='center')
                ax.set_title(title)
                self._cache[cache_key] = fig
                return fig

            # Fréquence brute
            freq_counts = Counter([word for doc in cleaned for word in doc.split()])
            freq_top = set([w for w, _ in freq_counts.most_common(20)])

            # TF-IDF
            vectorizer = TfidfVectorizer(
                max_features=max_features,
                stop_words='english'
            )
            tfidf = vectorizer.fit_transform(cleaned)
            scores = tfidf.sum(axis=0).A1
            tfidf_top = set(vectorizer.get_feature_names_out()[:20])

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
            excluded = {
                "salt", "water", "oil", "sugar", "pepper", "butter", "flour",
                "olive oil", "vegetable oil", "all-purpose flour", "cup", "tablespoon","salt and pepper"
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
                    .alias("ingredient")
                )
                .filter(
                    ~pl.col("ingredient").is_in(excluded) &
                    (pl.col("ingredient") != "") &
                    (pl.col("ingredient").str.len_chars() > 2)
                )
            )

            counts = (
                ingredients_cleaned
                .group_by("ingredient")
                .agg(pl.len().alias("count"))
                .sort("count", descending=True)
                .head(top_n)
            )

            if counts.height == 0:
                fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})
                ax.text(0.5, 0.5, "Aucun ingrédient trouvé", ha='center', va='center')
                self._cache[cache_key] = fig
                return fig

            labels = counts["ingredient"].to_list()
            values = counts["count"].to_list()
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
