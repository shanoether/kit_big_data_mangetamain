"""Rating analysis page of the Streamlit app."""

import matplotlib.pyplot as plt
import polars as pl
import seaborn as sns
import streamlit as st

st.set_page_config(
    page_title="Rating Analysis",
    page_icon="🍳",
    layout="centered",
    initial_sidebar_state="expanded",
)
st.title("Rating")

if "data_loaded" in st.session_state and st.session_state.data_loaded:
    df_interactions_nna = st.session_state.df_interactions_nna
    df_total = st.session_state.df_total
    df_total_court = st.session_state.df_total_court
    proportion_m = st.session_state.proportion_m
    proportion_s = st.session_state.proportion_s

    st.subheader("📊 Data Preview")

    # show first 10 rows of dataframe
    st.write("**Data from session_state:**")
    st.dataframe(df_interactions_nna.head(10))
    st.write(f"Shape: {df_interactions_nna.shape}")

    # draw histogram of ratings
    with st.spinner("Generating rating distribution..."):
        st.subheader("📈 Rating Distribution")
        fig, ax = plt.subplots()
        sns.histplot(df_interactions_nna["rating"], discrete=True, shrink=0.8, ax=ax)
        ax.set_title("Distribution of Ratings")
        ax.set_xlabel("Rating")
        ax.set_ylabel("Count")
        sns.despine()
        st.pyplot(fig)

    # draw boxplot of ratings
    st.subheader("📊 Rating Boxplot")
    with st.spinner("Generating rating boxplot..."):
        fig, ax = plt.subplots()
        ax.boxplot(df_interactions_nna["rating"].drop_nans(), vert=True)
        ax.set_title("Boxplot of Ratings")
        ax.set_ylabel("Values")

        # Show in Streamlit
        st.pyplot(fig)

    # Visualization of recipe distribution by review
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
        )  # log scale for better visualization
        ax.set_title("Distribution of number of reviews per recipe")
        ax.set_xlabel("Number of reviews")
        ax.set_ylabel("Number of recipes (log scale)")
        sns.despine()
        st.pyplot(fig)

    st.header("Time Evolution of Ratings")
    st.markdown(
        """
            This section shows how ratings have evolved over time.
            Use the slider below to filter by year range.
            """,
    )

    with st.spinner("Generating time evolution of ratings..."):
        min_year = df_interactions_nna["date"].dt.year().min()
        max_year = df_interactions_nna["date"].dt.year().max()

        # Streamlit slider for year selection
        year_range = st.slider(
            "Select year range",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
            step=1,
        )

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
        st.pyplot(fig_year)

    # Ratings vs Preparation Time
    st.header("Ratings vs Preparation Time")
    st.markdown(
        """
            This section explores the relationship between ratings and preparation time.
            """,
    )

    with st.spinner("Generating ratings vs preparation time charts..."):
        # Streamlit slider for rolling range selection
        rolling_range_time = st.slider(
            "Select width of rolling mean",
            min_value=1,
            max_value=10,
            value=5,
            step=1,
        )

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

    # Ratings vs Number of Steps
    st.header("Ratings vs Number of Steps")
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

else:
    st.error("❌ Data not loaded properly. Please refresh the page.")
