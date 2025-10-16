import streamlit as st
import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt

from mangetamain.utils.logger import get_logger

logger = get_logger()

st.set_page_config(
    page_title="Recipes Analysis",
    page_icon="🍲",
    layout="centered",    
    initial_sidebar_state="expanded"
)
st.title("Recipes analysis")

if 'data_loaded' in st.session_state and st.session_state.data_loaded:
    df_interactions = st.session_state.df_interactions
    df_recipes = st.session_state.df_recipes

    # Distribution des notes
    st.subheader("Distribution des notes")
    fig, ax = plt.subplots()
    sns.countplot(x="rating", data=df_interactions.to_pandas(), ax=ax)
    st.pyplot(fig)

    # Top recettes
    st.subheader("Top recettes les plus commentées")
    nb_recettes = st.slider("Nombre de recettes à afficher", 5, 30, 30)

    top_recipes = (
        df_interactions
        .group_by("recipe_id")
        .agg(pl.count().alias("nb_reviews"))
        .sort("nb_reviews", descending=True)
        .head(nb_recettes)
        .join(df_recipes.select(["recipe_id", "name"]), left_on="recipe_id", right_on="recipe_id", how="left")
    )
    logger.info(f"top_recipes shape: {top_recipes.shape}")
    logger.info(f"top_recipes sample: {top_recipes.head()}")
    logger.info(f"df_recipes sample: {df_recipes.head()}")
    logger.info(f"df_interactions sample: {df_interactions.head()}")
    toprint = df_recipes.filter(pl.col('recipe_id') == 2886)
    logger.info(f"df_recipes 2886: {toprint}")
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.barplot(data=top_recipes.to_pandas(), x="nb_reviews", y="name", palette='viridis', ax=ax)
    st.pyplot(fig)

    # Moyenne des notes
    st.subheader("Recettes les moins biens notéess")
    filtered = (
        df_interactions
        .group_by("recipe_id")
        .agg([
            pl.col("rating").mean().alias("mean_rating"),
            pl.count().alias("nb_reviews")
        ])
        .filter(pl.col("nb_reviews") >= 5)
        .join(df_recipes.select(["recipe_id", "name"]), left_on="recipe_id", right_on="recipe_id", how="left")
        .sort("mean_rating", descending=False)
        .head(nb_recettes)
    )

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.barplot(data=filtered.to_pandas(), x="mean_rating", y="name", ax=ax, palette="crest")
    st.pyplot(fig)
