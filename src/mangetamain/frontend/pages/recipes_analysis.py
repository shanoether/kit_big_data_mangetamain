"""Recipe Analysis for the Streamlit app."""

import matplotlib.pyplot as plt
import polars as pl
import seaborn as sns
import streamlit as st

from mangetamain.utils.logger import get_logger

logger = get_logger()


def display_wordclouds():
    st.header("🗣️ WordClouds (6 graphiques)")

    categories = [
        ("Recettes les plus commentées", None),
        ("Recettes mieux notées", "best"),
        ("Recettes moins bien notées", "worst")
    ]

    # Grille 2x3 pour les 6 wordclouds
    for i, (title, filter_type) in enumerate(categories):
        st.subheader(title)
        cols = st.columns(2)

        with cols[0]:
            with st.spinner(f"Génération WordCloud (Fréquence) pour {title}..."):
                recipe_ids = recipe_analyzer.get_top_recipe_ids(
                    n=review_count,
                    rating_filter=filter_type
                )
                reviews = recipe_analyzer.get_reviews_for_recipes(recipe_ids)
                fig = recipe_analyzer.plot_word_frequency(
                    reviews,
                    f"Fréquence - {title}",
                    freq_words
                )
                st.pyplot(fig)

            with cols[1]:
                with st.spinner(f"Génération WordCloud (TF-IDF) pour {title}..."):
                    fig = recipe_analyzer.plot_tfidf(
                        reviews,
                        f"TF-IDF - {title}",
                        freq_words
                    )
                    st.pyplot(fig)

   # Fonction pour afficher les comparaisons avec sabliers
def display_comparisons():
    st.header("🔄 Comparaisons Fréquence/TF-IDF (3 graphiques)")

    categories = [
        ("Recettes les plus commentées", None),
        ("Recettes mieux notées", "best"),
        ("Recettes moins bien notées", "worst")
    ]

    # Grille 1x3 pour les 3 comparaisons
    cols = st.columns(3)
    for i, (title, filter_type) in enumerate(categories):
        with cols[i]:
            with st.spinner(f"Comparaison pour {title}..."):
                recipe_ids = recipe_analyzer.get_top_recipe_ids(
                    n=review_count,
                    rating_filter=filter_type
                )
                reviews = recipe_analyzer.get_reviews_for_recipes(recipe_ids)
                fig = recipe_analyzer.compare_frequency_and_tfidf(
                    reviews,
                    f"Comparaison - {title}",
                    freq_words
                )
                st.pyplot(fig)


st.set_page_config(
    page_title="Recipes Analysis",
    page_icon="🍲",
    layout="centered",
    initial_sidebar_state="expanded",
)
st.title("Recipes analysis")

if "data_loaded" in st.session_state and st.session_state.data_loaded:
    df_interactions = st.session_state.df_interactions
    df_recipes = st.session_state.df_recipes
    recipe_analyzer = st.session_state.recipe_analyzer

    # Distribution des notes
    st.subheader("Distribution des notes")
    fig, ax = plt.subplots()
    sns.countplot(x="rating", data=df_interactions.to_pandas(), ax=ax)
    st.pyplot(fig)

    # Top recettes
    st.subheader("Top recettes les plus commentées")
    nb_recettes = st.slider("Nombre de recettes à afficher", 5, 30, 30)

    top_recipes = (
        df_interactions.group_by("recipe_id")
        .agg(pl.len().alias("nb_reviews"))
        .sort("nb_reviews", descending=True)
        .head(nb_recettes)
        .join(
            df_recipes.select(["recipe_id", "name"]),
            left_on="recipe_id",
            right_on="recipe_id",
            how="left",
        )
    )

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.barplot(
        data=top_recipes.to_pandas(),
        x="nb_reviews",
        y="name",
        palette="viridis",
        ax=ax,
    )
    st.pyplot(fig)

    # Moyenne des notes
    st.subheader("Recettes les moins biens notéess")
    NB_REVIEW_MIN = 5
    filtered = (
        df_interactions.group_by("recipe_id")
        .agg(
            [
                pl.col("rating").mean().alias("mean_rating"),
                pl.len().alias("nb_reviews"),
            ],
        )
        .filter(pl.col("nb_reviews") >= NB_REVIEW_MIN)
        .join(
            df_recipes.select(["recipe_id", "name"]),
            left_on="recipe_id",
            right_on="recipe_id",
            how="left",
        )
        .sort("mean_rating", descending=False)
        .head(nb_recettes)
    )

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.barplot(
        data=filtered.to_pandas(),
        x="mean_rating",
        y="name",
        ax=ax,
        palette="crest",
    )
    st.pyplot(fig)


### --- Mat modif

    ingredient_count = st.slider(
        "Nombre d'ingrédients",
        min_value=10,
        max_value=35,
        value=20
    )

    review_count = st.slider(
        "Nombre de recettes",
        min_value=20,
        max_value=500,
        value=100
    )

    freq_words = st.slider(
        "Mots max dans WordClouds",
        min_value=30,
        max_value=200,
        value=100
    )

    # Boutons pour afficher/masquer les sections
    st.sidebar.header("Affichage")
    show_ingredients = st.sidebar.checkbox("Top ingrédients", value=True)
    show_wordclouds = st.sidebar.checkbox("WordClouds (6)", value=True)
    show_comparisons = st.sidebar.checkbox("Comparaisons (3)", value=True)


    # Fonction pour afficher les wordclouds avec sabliers
    
 
    if show_ingredients:
        with st.spinner("Calcul des ingrédients..."):
            st.header("🍳 Top ingrédients utilisés")
            fig = recipe_analyzer.plot_top_ingredients(ingredient_count)
            st.pyplot(fig)

    if show_wordclouds:
        display_wordclouds()

    if show_comparisons:
        display_comparisons()

    # Informations supplémentaires
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Paramètres actuels:**")
    st.sidebar.markdown(f"- Recettes analysées: {review_count}")
    st.sidebar.markdown(f"- Mots par nuage: {freq_words}")
    st.sidebar.markdown(f"- Ingrédients: {ingredient_count}")

    st.markdown("---")
    st.caption("© 2025 - Analyse de données culinaires")
