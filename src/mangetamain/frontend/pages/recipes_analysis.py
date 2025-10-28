"""Recipe Analysis for the Streamlit app."""

import matplotlib.pyplot as plt
import polars as pl
import seaborn as sns
import streamlit as st

from mangetamain.utils.logger import get_logger

logger = get_logger()

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Recipes Analysis",
    page_icon="🍲",
    layout="centered",
    initial_sidebar_state="expanded",
)
st.title("Recipes Analysis")

# =============================================================================
# DATA LOADING AND VALIDATION
# =============================================================================

# Check if data has been loaded in the session state
if "data_loaded" in st.session_state and st.session_state.data_loaded:
    df_total_nt = st.session_state.df_total_nt
    df_interactions = st.session_state.df_interactions
    df_recipes = st.session_state.df_recipes
    recipe_analyzer = st.session_state.recipe_analyzer

    st.subheader("Top Most Reviewed Recipes")

    # User input: number of recipes to display
    nb_recipes = st.slider("Number of recipes to display", 5, 30, 30)

    # Aggregate reviews by recipe_id, count them, and join with recipe names
    top_recipes = (
        df_total_nt.group_by("name")
        .agg(
            pl.len().alias("nb_reviews"),
        )
        .sort("nb_reviews", descending=True)
        .head(nb_recipes)
    )

    # Display horizontal bar chart of most reviewed recipes
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.barplot(
        data=top_recipes,
        x="nb_reviews",
        y="name",
        palette="viridis",
        ax=ax,
        hue="name",
        legend=False,
    )
    ax.set_xlabel("Number of Reviews")
    ax.set_ylabel("")
    sns.despine()
    st.pyplot(fig)

    # =========================================================================
    # SECTION 3: LOWEST RATED RECIPES
    # =========================================================================

    st.subheader("Lowest Rated Recipes")

    # Minimum number of reviews required to be included in the analysis
    MIN_REVIEWS = 5

    # Moyenne des notes
    nb_worst = st.slider(
        "Number of recipes to display",
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

    # Display horizontal bar chart of lowest rated recipes
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.barplot(
        data=worst_recipes,
        x="mean_rating",
        y="name",
        ax=ax,
        palette="viridis",
        hue="name",
        legend=False,
    )
    ax.set_xlabel("Average Rating")
    ax.set_ylabel("")
    sns.despine()
    st.pyplot(fig)

    # =========================================================================
    # SECTION 4: USER CONTROLS - SLIDERS
    # =========================================================================

    # Slider for number of top ingredients to display
    ingredient_count = st.slider(
        "Number of ingredients",
        min_value=10,
        max_value=35,
        value=20,
    )

    # =========================================================================
    # SIDEBAR: SECTION VISIBILITY CONTROLS
    # =========================================================================

    # Checkboxes to show/hide different sections
    st.sidebar.header("Display Options")
    show_ingredients = st.sidebar.checkbox("Top Ingredients", value=True)
    show_wordclouds = st.sidebar.checkbox("WordClouds (6)", value=True)
    show_comparisons = st.sidebar.checkbox("Venn Comparisons (3)", value=True)

    # =========================================================================
    # SECTION 5: TOP INGREDIENTS VISUALIZATION
    # =========================================================================

    if show_ingredients:
        with st.spinner("Computing top ingredients..."):
            st.header("🍳 Top Ingredients Used")
            # Generate radar chart showing most common ingredients
            fig = recipe_analyzer.plot_top_ingredients(ingredient_count)
            st.pyplot(fig)

    # =========================================================================
    # SECTION 6: WORD CLOUDS VISUALIZATION
    # =========================================================================

    # Slider for number of recipes to analyze for word clouds
    recipe_count = st.slider(
        "Number of recipes",
        min_value=20,
        max_value=500,
        value=100,
    )

    # Slider for maximum words in word clouds
    wordcloud_max_words = st.slider(
        "Max words in WordClouds",
        min_value=30,
        max_value=200,
        value=100,
    )

    if show_wordclouds:
        with st.spinner("Generating word clouds..."):
            st.header("🍳 Ingredient Analysis")
            st.markdown(
                "Most Present Ingredient in Function of the Recipe Rating based on frequency (left) or on a TF-IDF metric (right)."
            )
            # Generate word clouds from recipe reviews
            recipe_analyzer.display_wordclouds(wordcloud_max_words)

    # =========================================================================
    # SECTION 7: VENN DIAGRAM COMPARISONS
    # =========================================================================

    if show_comparisons:
        with st.spinner("Computing Venn diagram comparisons..."):
            st.header("🍳 Venn Diagram Comparisons")
            # Compare frequency-based vs TF-IDF word extraction
            recipe_analyzer.display_comparisons(recipe_count, wordcloud_max_words)

    # =========================================================================
    # SIDEBAR: CURRENT PARAMETERS SUMMARY
    # =========================================================================

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Current Parameters:**")
    st.sidebar.markdown(f"- Recipes analyzed: {recipe_count}")
    st.sidebar.markdown(f"- Words per cloud: {wordcloud_max_words}")
    st.sidebar.markdown(f"- Ingredients: {ingredient_count}")

    # =========================================================================
    # FOOTER
    # =========================================================================
