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
    df_total_nt = st.session_state.df_total_nt

    # Top recettes
    st.subheader("Top recettes les plus commentées")
    nb_top = st.slider("Nombre de recettes à afficher", 5, 30, 20, key="nb_top_recipes")

    top_recipes = (
        df_total_nt.group_by("name")
        .agg(
            pl.len().alias("nb_reviews"),
        )
        .sort("nb_reviews", descending=True)
        .head(nb_top)
    )

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.barplot(data=top_recipes, x="nb_reviews", y="name", palette="viridis", ax=ax)
    st.pyplot(fig)

    # Moyenne des notes
    st.subheader("Recettes les moins biens notées")
    nb_worst = st.slider(
        "Nombre de recettes à afficher",
        5,
        30,
        20,
        key="nb_worst_recipes",
    )
    NB_REVIEW_MIN = 5
    worst_recipes = (
        df_total_nt.group_by("name")
        .agg(
            [
                pl.col("rating").mean().alias("mean_rating"),
                pl.len().alias("nb_reviews"),
            ],
        )
        .filter(pl.col("nb_reviews") >= NB_REVIEW_MIN)
        .sort("mean_rating")
        .head(nb_worst)
    )

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.barplot(data=worst_recipes, x="mean_rating", y="name", ax=ax, palette="viridis")
    st.pyplot(fig)
