"""Recipe Analysis for the Streamlit app."""

import matplotlib.pyplot as plt
import polars as pl
import seaborn as sns
import streamlit as st
from matplotlib.figure import Figure

from mangetamain.backend.recipe_analyzer import RecipeAnalyzer
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


@st.cache_data(show_spinner="Computing top recipes...")  # type: ignore[misc]
def compute_top_recipes(_df_total_nt: pl.DataFrame, nb_recipes: int) -> pl.DataFrame:
    """Compute most reviewed recipes (cached by nb_recipes).

    Args:
        _df_total_nt: DataFrame with recipe interactions
        nb_recipes: Number of top recipes to return

    Returns:
        DataFrame with name and nb_reviews columns
    """
    return (
        _df_total_nt.group_by("name")
        .agg(pl.len().alias("nb_reviews"))
        .sort("nb_reviews", descending=True)
        .head(nb_recipes)
    )


@st.cache_data(show_spinner="Computing lowest rated recipes...")  # type: ignore[misc]
def compute_worst_recipes(
    _df_total_nt: pl.DataFrame,
    nb_worst: int,
    min_reviews: int = 5,
) -> pl.DataFrame:
    """Compute lowest rated recipes (cached by nb_worst).

    Args:
        _df_total_nt: DataFrame with recipe interactions
        nb_worst: Number of worst recipes to return
        min_reviews: Minimum number of reviews required

    Returns:
        DataFrame with name, mean_rating, and nb_reviews columns
    """
    return (
        _df_total_nt.group_by("name")
        .agg(
            [
                pl.col("rating").mean().alias("mean_rating"),
                pl.len().alias("nb_reviews"),
            ],
        )
        .filter(pl.col("nb_reviews") >= min_reviews)
        .sort("mean_rating")
        .head(nb_worst)
    )


@st.cache_data(show_spinner="Generating ingredient radar chart...")  # type: ignore[misc]
def get_top_ingredients_plot(
    _recipe_analyzer: RecipeAnalyzer,
    ingredient_count: int,
) -> Figure:
    """Cached wrapper for recipe_analyzer.plot_top_ingredients.

    Args:
        _recipe_analyzer: RecipeAnalyzer instance (prefixed with _ to avoid hashing)
        ingredient_count: Number of top ingredients to display

    Returns:
        Matplotlib figure with polar plot
    """
    return _recipe_analyzer.plot_top_ingredients(ingredient_count)


@st.cache_data(show_spinner="Generating word clouds...")  # type: ignore[misc]
def get_wordcloud_figures(
    _recipe_analyzer: RecipeAnalyzer,
    wordcloud_max_words: int,
    filter_type: str,
    title: str,
) -> Figure:
    """Cached wrapper for individual word cloud generation.

    Args:
        _recipe_analyzer: RecipeAnalyzer instance
        wordcloud_max_words: Max words in cloud
        filter_type: Type of filter ('most', 'best', 'worst')
        title: Title for the plot

    Returns:
        Matplotlib figure with word cloud
    """
    return _recipe_analyzer.plot_word_cloud(wordcloud_max_words, filter_type, title)


@st.cache_data(show_spinner="Generating TF-IDF word clouds...")  # type: ignore[misc]
def get_tfidf_figures(
    _recipe_analyzer: RecipeAnalyzer,
    wordcloud_max_words: int,
    filter_type: str,
    title: str,
) -> Figure:
    """Cached wrapper for TF-IDF word cloud generation.

    Args:
        _recipe_analyzer: RecipeAnalyzer instance
        wordcloud_max_words: Max words in cloud
        filter_type: Type of filter ('most', 'best', 'worst')
        title: Title for the plot

    Returns:
        Matplotlib figure with TF-IDF word cloud
    """
    return _recipe_analyzer.plot_tfidf(wordcloud_max_words, filter_type, title)


@st.cache_data(show_spinner="Generating Venn comparisons...")  # type: ignore[misc]
def get_comparison_figures(
    _recipe_analyzer: RecipeAnalyzer,
    recipe_count: int,
    wordcloud_max_words: int,
    filter_type: str,
    title: str,
) -> Figure:
    """Cached wrapper for Venn diagram comparison generation.

    Args:
        _recipe_analyzer: RecipeAnalyzer instance
        recipe_count: Number of recipes to analyze
        wordcloud_max_words: Max features for TF-IDF
        filter_type: Type of filter ('most', 'best', 'worst')
        title: Title for the plot

    Returns:
        Matplotlib figure with Venn diagram
    """
    return _recipe_analyzer.compare_frequency_and_tfidf(
        recipe_count,
        wordcloud_max_words,
        filter_type,
        title,
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

    # Use cached computation
    top_recipes = compute_top_recipes(df_total_nt, nb_recipes)

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

    # Average ratings
    nb_worst = st.slider(
        "Number of recipes to display",
        5,
        30,
        20,
        key="nb_worst_recipes",
    )
    NB_REVIEW_MIN = 5

    # Use cached computation
    worst_recipes = compute_worst_recipes(df_total_nt, nb_worst, NB_REVIEW_MIN)

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
        st.header("🍳 Top Ingredients Used")
        st.markdown(""" In addition, a radar chart was created to visualize the most common ingredients in the recipes.
        It shows a strong presence of fundamental elements such as onion, eggs, milk, and garlic, emphasizing their central role in most dishes.
        Ingredients such as parmesan cheese, lemon juice, honey, and vanilla reflect the diversity of recipes, ranging from savory dishes to sweet preparations.
        The prior filtering of generic terms (salt, water, oil, sugar) makes it possible to focus on ingredients with true descriptive value.
        This chart complements the textual analysis by offering a synthetic and visual overview of dominant culinary trends.
        """)
        # Use cached plot generation
        fig = get_top_ingredients_plot(recipe_analyzer, ingredient_count)
        st.pyplot(fig)

    # =========================================================================
    # SECTION 6: WORD CLOUDS VISUALIZATION
    # =========================================================================
    # SECTION 6: WORD CLOUDS VISUALIZATION
    # =========================================================================
    st.header("🍳 Ingredient Analysis")

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
        # Display word clouds using cached wrappers
        st.subheader("🗣️ WordClouds (6 charts)")

        st.markdown(
            """In this analysis, two distinct methods were used to generate word clouds from culinary recipes.
        The first method is based on the raw frequency of words, after a rigorous filtering process aimed at removing English stop words (the, and, of), verbs, as well as certain terms considered uninformative such as recipe, thing, or definitely.
        This approach highlights the most frequent words in the corpus. However, it has the disadvantage of overrepresenting generic terms, often at the expense of rarer but more meaningful words for the analysis.
        The second method uses TF-IDF (Term Frequency Inverse - Document Frequency), a technique that weights the importance of a word according to its frequency within a document and its rarity across the entire corpus.
        This weighting helps emphasize discriminative words — those that best characterize specific recipes. In practice, the texts are cleaned to remove punctuation, verbs, and stop words before being transformed into a TF-IDF matrix using the TfidfVectorizer function from scikit-learn.
        Only the words with the highest cumulative TF-IDF scores are retained for word cloud generation, ensuring a visual representation of the most relevant terms.
        """,
        )
        categories = [
            ("Most reviewed recipes", "most"),
            ("Best rated recipes", "best"),
            ("Worst rated recipes", "worst"),
        ]

        # 2x3 grid for the 6 wordclouds
        for _i, (title, filter_type) in enumerate(categories):
            st.markdown(title)
            cols = st.columns(2)

            with cols[0]:
                fig = get_wordcloud_figures(
                    recipe_analyzer,
                    wordcloud_max_words,
                    filter_type,
                    f"Frequency - {title}",
                )
                st.pyplot(fig)

            with cols[1]:
                fig = get_tfidf_figures(
                    recipe_analyzer,
                    wordcloud_max_words,
                    filter_type,
                    f"TF-IDF - {title}",
                )
                st.pyplot(fig)

    # =========================================================================
    # SECTION 7: VENN DIAGRAM COMPARISONS
    # =========================================================================

    st.header("🍳 Venn Diagram Comparisons")

    if show_comparisons:
        st.markdown(
            """ To compare both approaches, Venn diagrams were used.
            These charts provide a clear visualization of the intersections and differences between the selected word sets.
            The overlapping areas represent the words identified by both methods, often associated with basic vocabulary used to describe or comment on recipes.
            The words exclusive to the TF-IDF method reveal rarer or more specific terms, such as distinctive ingredients or particular cooking techniques.
            A strong overlap between the circles indicates convergence between the two methods, while a smaller intersection highlights divergences in word selection.
        """,
        )

        # Display Venn diagrams using cached wrapper
        st.subheader("🔄 Frequency/TF-IDF Comparisons (3 charts)")

        for _i, (title, filter_type) in enumerate(categories):
            st.markdown(title)
            fig = get_comparison_figures(
                recipe_analyzer,
                recipe_count,
                wordcloud_max_words,
                filter_type,
                f"Comparison - {title}",
            )
            st.pyplot(fig)

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
