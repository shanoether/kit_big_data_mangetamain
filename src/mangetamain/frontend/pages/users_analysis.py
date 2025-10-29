"""Users Analysis for the Streamlit app."""

import matplotlib.pyplot as plt
import polars as pl
import seaborn as sns
import streamlit as st

st.set_page_config(
    page_title="Users Analysis",
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

st.title("👥 Users Analysis")
st.markdown("""
This page provides an analysis of user behavior based on the interactions dataset.
You can explore the distribution of reviews per user, categorize users based on their activity,
and analyze average ratings given by users.
""")

if "data_loaded" in st.session_state and st.session_state.data_loaded:
    df_interactions = st.session_state.df_interactions_nna

    # Distribution of number of reviews per user
    st.markdown("---")
    st.subheader("Distribution of number of reviews per user")
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        reviews_per_user = df_interactions.group_by("user_id").agg(
            pl.len().alias("nb_reviews"),
        )

        fig, ax = plt.subplots()
        sns.histplot(
            reviews_per_user["nb_reviews"].to_pandas(),
            bins=30,
            log_scale=(False, True),
            ax=ax,
        )
        sns.despine()
        st.pyplot(fig)

    with col2:
        # User categorization
        st.subheader("User categorization")

        reviews_per_user_pd = reviews_per_user.to_pandas()

        def categorize_user(n: int) -> str:
            """Simple categorization of users based on number of reviews.

            Args:
                n: number of review per user.

            """
            OCC = 1
            REGULAR = 5
            ACTIVE = 20
            if n == OCC:
                return "Occasionnel (1 review)"
            elif n <= REGULAR:
                return "Régulier (2-5 reviews)"
            elif n <= ACTIVE:
                return "Actif (6-20 reviews)"
            else:
                return "Super-actif (>20 reviews)"

        user_categories = (
            reviews_per_user_pd["nb_reviews"].apply(categorize_user).value_counts()
        )

        fig, ax = plt.subplots()
        sns.barplot(
            x=user_categories.index,
            y=user_categories.values,
            ax=ax,
            palette="Blues_r",
            hue=user_categories.index,
        )
        plt.xticks(rotation=25)
        sns.despine()
        st.pyplot(fig)

    with col3:
        # Average rating per user
        st.subheader("Average rating per user")
        df_user_stats = df_interactions.group_by("user_id").agg(
            [
                pl.len().alias("nb_reviews"),
                pl.col("rating").mean().alias("mean_rating"),
            ],
        )
        fig, ax = plt.subplots()
        sns.scatterplot(
            data=df_user_stats.to_pandas(),
            x="nb_reviews",
            y="mean_rating",
            ax=ax,
        )
        sns.despine()
        st.pyplot(fig)
