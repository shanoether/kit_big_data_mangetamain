"""Rating analysis page of the Streamlit app."""

import matplotlib.pyplot as plt
import polars as pl
import seaborn as sns
import streamlit as st
from matplotlib.figure import Figure
from scipy import stats

st.set_page_config(
    page_title="Rating Analysis",
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

st.title("⭐ Rating")
st.markdown(
    """
    <div style="text-align: justify;">
    <p>
    This page presents an analysis of user ratings for recipes on the Mangetamain platform.
    We will explore the distribution of ratings,
    their evolution over time, and how they relate to recipe characteristics
    such as preparation time and number of steps
    </p>
    </div>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner="Performing Comprehensive Rating Analysis...")  # type: ignore[misc]
def comprehensive_rating_analysis(
    df: pl.DataFrame,
) -> tuple[pl.DataFrame, dict[str, float]]:
    """Comprehensive A/B test analysis between rating count and average rating."""
    # 1. Data aggregation by recipe
    df_agg = df.group_by("recipe_id").agg(
        [
            pl.col("rating").mean().alias("avg_rating"),
            pl.col("rating").count().alias("rating_count"),
            pl.col("user_id").n_unique().alias("unique_users"),
            pl.col("rating").std().alias("rating_std"),
        ]
    )

    # 2. Create A/B test groups based on rating count median
    median_count = df_agg["rating_count"].median()
    THRESHOLD_10 = 10
    THRESHOLD_25 = 25
    THRESHOLD_50 = 50
    THRESHOLD_100 = 100

    df_agg = df_agg.with_columns(
        [
            pl.when(pl.col("rating_count") > median_count)
            .then(pl.lit("High_Rating_Count"))
            .otherwise(pl.lit("Low_Rating_Count"))
            .alias("ab_group"),
            pl.when(pl.col("rating_count") <= THRESHOLD_10)
            .then(pl.lit("1-10"))
            .when(pl.col("rating_count") <= THRESHOLD_25)
            .then(pl.lit("11-25"))
            .when(pl.col("rating_count") <= THRESHOLD_50)
            .then(pl.lit("26-50"))
            .when(pl.col("rating_count") <= THRESHOLD_100)
            .then(pl.lit("51-100"))
            .otherwise(pl.lit("100+"))
            .alias("rating_segment"),
        ]
    )

    # 3. Statistical tests
    high_group = df_agg.filter(pl.col("ab_group") == "High_Rating_Count")["avg_rating"]
    low_group = df_agg.filter(pl.col("ab_group") == "Low_Rating_Count")["avg_rating"]

    # T-test
    t_stat, p_value_t = stats.ttest_ind(high_group, low_group, nan_policy="omit")

    # Mann-Whitney U test
    u_stat, p_value_mw = stats.mannwhitneyu(
        high_group, low_group, alternative="two-sided"
    )

    # Correlation analysis
    correlation = df_agg.select(pl.corr("rating_count", "avg_rating")).item()

    results = {
        "high_count_mean": high_group.mean(),
        "low_count_mean": low_group.mean(),
        "high_count_std": high_group.std(),
        "low_count_std": low_group.std(),
        "high_count_size": len(high_group),
        "low_count_size": len(low_group),
        "t_statistic": t_stat,
        "t_p_value": p_value_t,
        "u_statistic": u_stat,
        "mw_p_value": p_value_mw,
        "correlation": correlation,
        "median_rating_count": median_count,
    }

    return df_agg, results


@st.cache_data(show_spinner="Generating Scatter Plot...")  # type: ignore[misc]
def create_scatter_plot(df_agg: pl.DataFrame, results: dict[str, float]) -> Figure:
    """Create scatter plot: Rating Count vs Average Rating.

    Returns the matplotlib Figure object instead of showing it.
    """
    correlation = results["correlation"]

    fig, ax = plt.subplots(figsize=(10, 6))

    # Extraire les données Polars en numpy
    rating_count = df_agg["rating_count"].to_numpy()
    avg_rating = df_agg["avg_rating"].to_numpy()

    scatter = ax.scatter(
        rating_count, avg_rating, alpha=0.6, c=avg_rating, cmap="viridis"
    )

    ax.set_xlabel("Number of Ratings")
    ax.set_ylabel("Average Rating")
    ax.set_title(
        f"Relationship: Rating Count vs Average Rating\nCorrelation: {correlation:.3f}"
    )
    ax.grid(True, alpha=0.3)

    cbar = fig.colorbar(scatter, ax=ax)
    cbar.set_label("Average Rating")

    return fig


@st.cache_data(show_spinner="Generating Box Plot...")  # type: ignore[misc]
def create_box_plot(df_agg: pl.DataFrame, results: dict[str, float]) -> Figure:
    """Create box plot: A/B Group Comparison."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Extraire les données
    high_ratings = df_agg.filter(pl.col("ab_group") == "High_Rating_Count")[
        "avg_rating"
    ].to_numpy()
    low_ratings = df_agg.filter(pl.col("ab_group") == "Low_Rating_Count")[
        "avg_rating"
    ].to_numpy()

    box_data = [low_ratings, high_ratings]

    # Boxplot
    ax.boxplot(box_data, tick_labels=["Low Rating Count", "High Rating Count"])

    ax.set_ylabel("Average Rating")
    ax.set_title(
        f"A/B Test: Average Rating by Group\np-value: {results['t_p_value']:.4f}"
    )
    ax.grid(True, alpha=0.3)

    # Add mean markers
    ax.scatter(
        [1, 2],
        [results["low_count_mean"], results["high_count_mean"]],
        color="red",
        zorder=3,
        label="Mean",
        s=100,
    )
    ax.legend()

    return fig


@st.cache_data(show_spinner="Generating Distribution Plot...")  # type: ignore[misc]
def create_distribution_plot(df_agg: pl.DataFrame) -> Figure:
    """Create distribution plot of average ratings by group.

    Returns the matplotlib Figure object instead of showing it.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Extraire les données en numpy
    high_ratings = df_agg.filter(pl.col("ab_group") == "High_Rating_Count")[
        "avg_rating"
    ].to_numpy()
    low_ratings = df_agg.filter(pl.col("ab_group") == "Low_Rating_Count")[
        "avg_rating"
    ].to_numpy()

    # Histogrammes
    ax.hist(high_ratings, alpha=0.7, label="High Rating Count", bins=20, density=True)
    ax.hist(low_ratings, alpha=0.7, label="Low Rating Count", bins=20, density=True)

    ax.set_xlabel("Average Rating")
    ax.set_ylabel("Density")
    ax.set_title("Distribution of Average Ratings by Group")
    ax.legend()
    ax.grid(True, alpha=0.3)

    return fig


icon = "👉"

if "data_loaded" in st.session_state and st.session_state.data_loaded:
    df_interactions_nna = st.session_state.df_interactions_nna
    df_total = st.session_state.df_total
    df_total_court = st.session_state.df_total_court
    proportion_m = st.session_state.proportion_m
    proportion_s = st.session_state.proportion_s

    st.markdown("""---""")
    st.header(f"{icon} Rating Overview")
    st.subheader("Data Preview")

    # show first 10 rows of dataframe
    # st.write("**Data from session_state:**")
    with st.expander("Show sample of rating data"):
        st.dataframe(df_interactions_nna.head(10))
        st.write(f"Shape: {df_interactions_nna.shape}")

    col1, space, col2 = st.columns([1, 0.05, 1])
    # draw histogram of ratings
    with st.spinner("Generating rating distribution..."):
        fig, ax = plt.subplots()
        sns.histplot(df_interactions_nna["rating"], discrete=True, shrink=0.8, ax=ax)
        ax.set_title("Distribution of Ratings")
        ax.set_xlabel("Rating")
        ax.set_ylabel("Count")
        sns.despine()

        with col1:
            st.subheader("Rating Distribution")
            plt.tight_layout(rect=[0, 0, 1, 0.95])
            st.pyplot(fig)
            st.markdown(
                """
                <div style="text-align: justify;">
                <p>
                The rating distribution shows that the large majority of ratings are 5 stars,
                which means that there is a huge bias in all analysis related to ratings.
                This bias can be explained by the fact that users tend to rate only recipes
                they liked, and not the ones they didn't like. The problem is that we don't have
                any information about the recipes that were not rated, which makes it difficult
                to draw realistic conclusions from the ratings.
                </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # draw boxplot of ratings
    with st.spinner("Generating rating boxplot..."):
        fig, ax = plt.subplots()
        ax.boxplot(df_interactions_nna["rating"].drop_nans(), vert=True)
        ax.set_title("Boxplot of Ratings")
        ax.set_ylabel("Values")

        # Show in Streamlit
        with col2:
            st.subheader("Rating Boxplot")
            plt.tight_layout(rect=[0, 0, 1, 0.95])
            st.pyplot(fig)
            st.markdown(
                """
                <div style="text-align: justify;">
                <p>
                    The boxplot shows that the distribution is really skewed to the right,
                    since all votes below three are considered as outliers.w
                </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Visualization of recipe distribution by review
    st.subheader("Distribution of the number of reviews by recipe")
    st.markdown(
        """
                <div style="text-align: justify;">
                <p>
                This graphs how many reviews each recipe has received.
                We can see that most recipes have only a few reviews,
                while a few have many reviews.
                And there are a few reviews that were reviewed more than 500000 times!
                </p>
                </div>
                """,
        unsafe_allow_html=True,
    )
    with st.spinner("Generating rating distribution by review..."):
        reviews_per_recipe = df_interactions_nna.group_by("recipe_id").agg(
            pl.len().alias("review_count"),
        )
        fig, ax = plt.subplots()
        sns.histplot(
            reviews_per_recipe,
            bins=30,
            log_scale=(False, True),
            ax=ax,
        )  # échelle log pour mieux visualiser
        ax.set_title("Distribution of the number of reviews by recipe")
        ax.set_xlabel("Number of reviews")
        ax.set_ylabel("Number of recipes (log scale)")
        sns.despine()
        col1, col2, col3 = st.columns([1, 2.5, 1])
        with col2:
            st.pyplot(fig)

    st.markdown("""---""")
    st.header(f"{icon} Time Evolution of Ratings")
    st.markdown(
        """
            This section shows how ratings have evolved over time.
            Use the slider below to filter by year range.
            """,
    )

    min_year = df_interactions_nna["date"].dt.year().min()
    max_year = df_interactions_nna["date"].dt.year().max()

    # Streamlit slider for year selection
    col1, col2, col3 = st.columns([1, 2.5, 1])
    with col2:
        year_range = st.slider(
            "Select year range",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
            step=1,
        )

    with st.spinner("Generating time evolution of ratings..."):
        # Filter DataFrame based on slider
        filtered_interactions = df_interactions_nna.select(["date", "rating"]).filter(
            (pl.col("date").dt.year() >= year_range[0])
            & (pl.col("date").dt.year() <= year_range[1]),
        )

        # Time evolution of ratings (filtered)
        fig_year, ax_year = plt.subplots()
        sns.histplot(
            x=filtered_interactions["date"].dt.year(),
            hue=filtered_interactions["rating"],
            discrete=True,
            shrink=0.8,
        )
        ax_year.set_title("Time evolution of ratings")
        ax_year.set_xlabel("Year")
        ax_year.set_ylabel("Count by rating")
        plt.xticks(range(2000, 2019, 3))
        sns.despine()
        with col2:
            st.pyplot(fig_year)

    # Ratings vs Preparation Time
    st.markdown("""---""")
    st.header(f"{icon} Ratings vs Preparation Time")
    st.markdown(
        """
            This section explores the relationship between ratings and preparation time.
            """,
    )

    rolling_range_time = st.slider(
        "Select width of rolling mean",
        min_value=1,
        max_value=10,
        value=5,
        step=1,
    )

    with st.spinner("Generating ratings vs preparation time charts..."):
        # Streamlit slider for rolling range selection

        fig_time, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        sns.histplot(df_total_court, x="minutes", hue="rating", bins=20, ax=ax1)
        ax1.set_title("Ratings by Preparation Time")
        ax1.set_xlabel("Preparation Time (minutes)")
        ax1.set_ylabel("Count by rating")
        ax2.set_ylim((0, 1))
        ax2.plot(proportion_m.rolling_mean(rolling_range_time))
        ax2.set_title("Proportion of 5-star Ratings vs Preparation Time")
        ax2.set_xlabel("Preparation Time (minutes)")
        ax2.set_ylabel("Proportion of 5-star Ratings")
        ax2.grid()
        sns.despine()
        st.pyplot(fig_time)
        st.markdown(
            """
                It can be observed that the ratings do not appear to depend strongly
                on the preparation time. The proportion of 5-star ratings remains relatively
                stable.""",
        )

    # Ratings vs Number of Steps
    st.markdown("""---""")
    st.header(f"{icon} Ratings vs Number of Steps")
    st.markdown(
        """
            This section explores the relationship between ratings and number of steps in the recipe.
            """,
    )
    with st.spinner("Generating ratings vs number of steps charts..."):
        # Streamlit slider for rolling range selection
        rolling_range_steps = st.slider(
            "Select width of rolling mean",
            min_value=1,
            max_value=5,
            value=2,
            step=1,
        )

        fig_steps, (ax3, ax4) = plt.subplots(1, 2, figsize=(14, 5))
        NB_STEPS_MAX = 40
        sns.histplot(
            df_total.filter(pl.col("n_steps") <= NB_STEPS_MAX),
            x="n_steps",
            hue="rating",
            bins=20,
            ax=ax3,
        )
        ax3.set_title("Ratings by Number of Steps")
        ax3.set_xlabel("Number of Steps")
        ax3.set_ylabel("Count by rating")
        ax4.set_ylim((0, 1))
        ax4.plot(proportion_s.rolling_mean(rolling_range_steps))
        ax4.set_title("Proportion of 5-star Ratings vs Number of Steps")
        ax4.set_xlabel("Number of Steps")
        ax4.set_ylabel("Proportion of 5-star Ratings")
        ax4.grid()
        sns.despine()
        st.pyplot(fig_steps)
        st.markdown(
            """
                And we can also see that the proportion of 5-star rankings does not
                either depend on the number of steps in the recipe.
                """,
        )

    st.markdown("""---""")
    st.header(f"{icon} Average Ratings vs Number of Ratings")
    st.markdown(
        """
        <div style="text-align: justify;">
        <p>
        This section presents a comprehensive A/B test analysis
        to explore the relationship between the number of ratings
        a recipe has received and its average rating.
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.spinner("Performing comprehensive rating analysis..."):
        df_agg, results = comprehensive_rating_analysis(df_interactions_nna)
        scatter_fig = create_scatter_plot(df_agg, results)
        box_fig = create_box_plot(df_agg, results)
        dist_fig = create_distribution_plot(df_agg)

        col1, _, col2 = st.columns([1, 0.05, 1])
        with col1:
            # st.subheader("Box Plot: A/B Group Comparison")
            st.markdown(
                """
                    <h4 style="text-align: center;">
                        Box Plot: A/B Group Comparison
                    </h4>
                    """,
                unsafe_allow_html=True,
            )

            box_fig.tight_layout(rect=[0, 0, 1, 0.95])
            st.pyplot(box_fig)
        with col2:
            # st.subheader("Distribution Plot: Average Ratings by Group")
            st.markdown(
                """
                    <h4 style="text-align: center;">
                        Distribution Plot: Average Ratings by Group
                    </h4>
                    """,
                unsafe_allow_html=True,
            )
            dist_fig.tight_layout(rect=[0, 0, 1, 0.95])
            st.pyplot(dist_fig)

        st.markdown(
            """
            <div style="text-align: justify;">
            <p>
            In this A/B test analysis,
            the dataset was divided into two groups
            based on the number of ratings (rating count)
            for each recipe, using the median value as the threshold.
            Specifically:

            - **Group A (High Rating Count)**:
            includes recipes with a number of ratings
            greater than the median.

            - **Group B (Low Rating Count)**:
            includes recipes with a number of ratings
            less than or equal to the median.

            The comparison of the average rating scores
            between these two groups is represented in the box plot.
            This chart shows a clear difference in the
            distribution of scores between the two groups.
            More importantly, a p-value = 0
            (in practice, p-value < 0.0001) confirms that
            this difference is highly statistically significant -
            meaning the probability that this difference
            occurred by random chance is extremely low.
            This indicates that, from a statistical standpoint,
            recipes with more ratings genuinely tend to
            receive higher average scores than those with
            fewer ratings.
            </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        _, col1, _ = st.columns([1, 3, 1])
        with col1:
            st.markdown(
                """
                    <h4 style="text-align: center;">
                        Scatter Plot: Rating Count vs Average Rating
                    </h4>
                    """,
                unsafe_allow_html=True,
            )
            # st.subheader("Scatter Plot: Rating Count vs Average Rating")
            st.pyplot(scatter_fig)

        st.markdown(
            """
            <div style="text-align: justify;">
            <p>
            The scatter plot depicting the direct relationship
            between the number of ratings and the average
            rating score, however, presents a different picture.
            The correlation coefficient of 0.018 - a value
            very close to zero - indicates an almost non-existent
            linear relationship between the two variables.
            This result implies that an increase in the number
            of ratings is not accompanied by a clear,
            consistent change in the average score.
            Therefore, although the A/B test identifies a
            significant difference between the two groups
            divided by the median, the intrinsic relationship
            between these two factors across the entire dataset
            remains very weak and non-linear.
            </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.error("❌ Data not loaded properly. Please refresh the page.")
