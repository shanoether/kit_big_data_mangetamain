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
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(
    """
    <style>
    p { font-size: 1.2rem !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🍳 Recipes Analysis")
st.markdown("""
            Deep dive into recipe characteristics and ingredients.
            Explore popular recipes, ratings, and ingredient trends.
            """)

st.markdown("""---""")

# =============================================================================
# DATA LOADING AND VALIDATION
# =============================================================================

icon = "👉"

# Check if data has been loaded in the session state
if "data_loaded" in st.session_state and st.session_state.data_loaded:
    df_total_nt = st.session_state.df_total_nt
    df_interactions = st.session_state.df_interactions
    df_recipes = st.session_state.df_recipes
    recipe_analyzer = st.session_state.recipe_analyzer

    st.header(f"{icon} Recipes Popularity")

    col1, spacer, col2 = st.columns([1, 0.1, 1])
    with col1:
        st.subheader("Top Most Reviewed Recipes")

        # User input: number of recipes to display
        nb_recipes = st.slider("Number of recipes to display", 5, 30, 30)
        with st.spinner("Generating chart..."):
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

    with col2:
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
        with st.spinner("Generating chart..."):
            worst_recipes = (
                df_total_nt.group_by("name")
                .agg(
                    [
                        pl.col("rating").mean().alias("mean_rating"),
                        pl.len().alias("nb_reviews"),
                    ],
                )
                .filter(pl.col("nb_reviews") >= MIN_REVIEWS)
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

    st.markdown("""---""")

    # =========================================================================
    # SECTION 4: USER CONTROLS - SLIDERS
    # =========================================================================

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
        # Slider for number of top ingredients to display
        st.header(f"{icon} Top Ingredients Used")

        ingredient_count = st.slider(
            "Number of ingredients",
            min_value=10,
            max_value=35,
            value=20,
        )
        with st.spinner("Computing top ingredients..."):
            # st.markdown(""" In addition, a radar chart was created to visualize the most common ingredients in the recipes.
            # It shows a strong presence of fundamental elements such as onion, eggs, milk, and garlic, emphasizing their central role in most dishes.
            # Ingredients such as parmesan cheese, lemon juice, honey, and vanilla reflect the diversity of recipes, ranging from savory dishes to sweet preparations.
            # The prior filtering of generic terms (salt, water, oil, sugar) makes it possible to focus on ingredients with true descriptive value.
            # This chart complements the textual analysis by offering a synthetic and visual overview of dominant culinary trends.
            # """)
            # Generate radar chart showing most common ingredients

            col_text, col_chart = st.columns([2, 1.5])

            with col_text:
                st.markdown(
                    """
                    <div style="text-align: justify;">
                    <p>

                    - In addition, a radar chart was created to visualize the most common ingredients in the recipes.
                    It shows a strong presence of fundamental elements such as onion, eggs, milk, and garlic,
                    emphasizing their central role in most dishes.

                    - Ingredients such as parmesan cheese, lemon juice, honey, and vanilla reflect the diversity of recipes,
                    ranging from savory dishes to sweet preparations. The prior filtering of generic terms
                    (salt, water, oil, sugar) focuses on ingredients with true descriptive value.
                    This chart complements the textual analysis by offering a synthetic and visual overview
                    of dominant culinary trends.
                    </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col_chart:
                fig = recipe_analyzer.plot_top_ingredients(ingredient_count)
                st.pyplot(fig)

        st.markdown("""---""")

    # =========================================================================
    # SECTION 6: WORD CLOUDS VISUALIZATION
    # =========================================================================

    if show_wordclouds:
        st.header(f"{icon} Ingredient Analysis")
        st.markdown(
            """
            <div style="text-align: justify;">
            <p>
            In this analysis, two distinct methods were used to generate word clouds from culinary recipes.

            - The first method is based on the **raw frequency of words**,
            after a rigorous filtering process aimed at removing English stop words (the, and, of), verbs,
            as well as certain terms considered uninformative such as *recipe*, *thing*, or *definitely*.
            This approach highlights the most frequent words in the corpus.
            However, it has the disadvantage of overrepresenting generic terms,
            often at the expense of rarer but more meaningful words for the analysis.

            - The second method uses **TF-IDF (Term Frequency-Inverse Document Frequency)**,
            a technique that weights the importance of a word according to its frequency
            within a document and its rarity across the entire corpus.
            This weighting helps emphasize discriminative words -
            those that best characterize specific recipes.

            In practice, the texts are cleaned to remove punctuation, verbs, and
            stop words before being transformed into a TF-IDF matrix using
            the **TfidfVectorizer** function from scikit-learn.
            Only the words with the highest cumulative TF-IDF scores are retained for word cloud
            generation, ensuring a visual representation of the most relevant terms.
            </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Slider for number of recipes to analyze for word clouds
        col1, space, col2 = st.columns([1, 0.05, 1])
        with col1:
            recipe_count = st.slider(
                "Number of recipes",
                min_value=20,
                max_value=500,
                value=100,
            )
        # Slider for maximum words in word clouds
        with col2:
            wordcloud_max_words = st.slider(
                "Max words in WordClouds",
                min_value=30,
                max_value=200,
                value=100,
            )

        # Generate word clouds from recipe reviews
        recipe_analyzer.display_wordclouds(wordcloud_max_words)
        st.markdown("""---""")

        # =========================================================================
        # SECTION 7: VENN DIAGRAM COMPARISONS
        # =========================================================================
        if show_comparisons:
            st.header(f"{icon} Venn Diagram Comparisons")
            st.markdown(
                """
                <div style="text-align: justify;">
                <p>To compare both approaches, Venn diagrams were used.
                These charts provide a clear visualization of the intersections
                and differences between the selected word sets.

                The overlapping areas represent the words identified by both methods,
                often associated with basic vocabulary used to describe
                or comment on recipes.
                The words exclusive to the TF-IDF method reveal rarer or
                more specific terms, such as distinctive ingredients or
                particular cooking techniques.
                A strong overlap between the circles indicates convergence
                between the two methods, while a smaller intersection highlights
                divergences in word selection.
                </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            # Compare frequency-based vs TF-IDF word extraction
            recipe_analyzer.display_comparisons(
                recipe_count,
                wordcloud_max_words,
            )

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
