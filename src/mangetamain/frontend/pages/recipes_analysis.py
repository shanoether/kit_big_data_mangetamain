"""Recipe Analysis for the Stremalit app."""

import matplotlib.pyplot as plt
import polars as pl
import seaborn as sns
import streamlit as st

from mangetamain.utils.logger import get_logger

logger = get_logger()

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

    # Distribution des notes
    st.subheader("Distribution des notes")
    with st.spinner("Generating rating distribution chart..."):
        fig, ax = plt.subplots()
        sns.countplot(x="rating", data=df_interactions.to_pandas(), ax=ax)
        st.pyplot(fig)

    # Top recettes
    st.subheader("Top recettes les plus commentées")
    nb_top = st.slider("Nombre de recettes à afficher", 5, 30, 20, key="slider_top_commented")
    
    top_recipes = (
        df_interactions.group_by("recipe_id")
        .agg(pl.len().alias("nb_reviews"))
        .sort("nb_reviews", descending=True)
        .head(nb_top)
        .join(df_recipes.select(["id", "name"]), left_on="recipe_id", right_on="id", how="left")
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
    st.subheader("Recettes les moins bien notées")
    nb_worst = st.slider("Nombre de recettes à afficher (worst)", 5, 30, 20, key="slider_worst_rated")

    filtered = (
        df_interactions
        .group_by("recipe_id")
        .agg([
            pl.col("rating").mean().alias("mean_rating"),
            pl.count().alias("nb_reviews")
        ])
        .filter(pl.col("nb_reviews") >= 5)
        .join(
            df_recipes.select(["id", "name"]),
            left_on="recipe_id", right_on="id", how="left"
        )
        .sort("mean_rating", descending=False)
        .head(nb_worst)
    )

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.barplot(
        data=filtered.to_pandas(),
        x="mean_rating", y="name",
        palette="rocket", ax=ax
    )
    ax.set_xlabel("Note moyenne")
    ax.set_ylabel("Recette")
    st.pyplot(fig)

