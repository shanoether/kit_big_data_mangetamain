"""Rating analysis page of the Streamlit app."""

import matplotlib.pyplot as plt
import polars as pl
import seaborn as sns
import streamlit as st

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
                    since all votes below three are considered as outliers.
                </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Visualization of recipe distribution by review
    st.subheader("Distribution of the number of reviews by recipe")
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

else:
    st.error("❌ Data not loaded properly. Please refresh the page.")
