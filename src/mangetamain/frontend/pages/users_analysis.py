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
            User behavior patterns and engagement metrics
            """)


@st.cache_data(show_spinner="Computing user statistics...")  # type: ignore[misc]
def compute_reviews_per_user(_df_interactions: pl.DataFrame) -> pl.DataFrame:
    """Compute number of reviews per user (cached).

    Args:
        _df_interactions: DataFrame with interactions data

    Returns:
        DataFrame with user_id and nb_reviews columns
    """
    return _df_interactions.group_by("user_id").agg(
        pl.len().alias("nb_reviews"),
    )


@st.cache_data(show_spinner="Computing user ratings...")  # type: ignore[misc]
def compute_user_stats(_df_interactions: pl.DataFrame) -> pl.DataFrame:
    """Compute user statistics including mean rating (cached).

    Args:
        _df_interactions: DataFrame with interactions data

    Returns:
        DataFrame with user_id, nb_reviews, and mean_rating columns
    """
    return _df_interactions.group_by("user_id").agg(
        [
            pl.len().alias("nb_reviews"),
            pl.col("rating").mean().alias("mean_rating"),
        ],
    )


st.markdown(
    """
    This page provides an analysis of user behavior on the Mangetamain platform.
    We will explore the distribution of reviews per user,
    categorize users based on their activity levels,
    and examine the relationship between user activity and average ratings."""
)

if "data_loaded" in st.session_state and st.session_state.data_loaded:
    df_interactions = st.session_state.df_interactions_nna

    # Distribution of number of reviews per user
    st.subheader("Distribution of number of reviews per user")
    reviews_per_user = compute_reviews_per_user(df_interactions)

    fig, ax = plt.subplots()
    sns.histplot(
        reviews_per_user["nb_reviews"].to_pandas(),
        bins=30,
        log_scale=(False, True),
        ax=ax,
    )
    sns.despine()

    st.pyplot(fig)
    plt.close(fig)  # Free memory fig
    st.markdown(
        """
        This graph shows a highly unbalanced distribution: the majority of recipes have only a small number of reviews,
        while a minority attract a huge number of comments. This illustrates a "long tail" phenomenon where a handful
        of very popular recipes generate a large part of the activity, while most remain largely unrated.
        On a logarithmic scale, this inequality becomes more visible.

        The majority of users leave only one review, indicating many are occasional users. In contrast, a minority of
        very active users produce a large volume of comments. This reflects a two-tiered community: many passive
        consumers and a few loyal contributors. We observe that someone has made approximately 7,500 reviews—likely
        either a bot or an enthusiast.
        """,
    )

    # User categorization
    st.subheader("User categorization")


@st.cache_data  # type: ignore[misc]
def categorize_users(_reviews_per_user: pl.DataFrame) -> pl.Series:
    """Categorize users by number of reviews (cached).

    Args:
        _reviews_per_user: DataFrame with nb_reviews column

    Returns:
        Series with categorized user counts
    """
    reviews_per_user_pd = _reviews_per_user.to_pandas()

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

    return reviews_per_user_pd["nb_reviews"].apply(categorize_user).value_counts()


if "data_loaded" in st.session_state and st.session_state.data_loaded:
    df_interactions = st.session_state.df_interactions_nna

    # Distribution of number of reviews per user
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Distribution of reviews per user")
        reviews_per_user = compute_reviews_per_user(df_interactions)

        fig, ax = plt.subplots()
        sns.histplot(
            reviews_per_user["nb_reviews"].to_pandas(),
            bins=30,
            log_scale=(False, True),
            ax=ax,
        )
        sns.despine()
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        st.pyplot(fig)
        plt.close(fig)  # Free memory fig

    with col2:
        st.subheader("User categorization")

        user_categories = categorize_users(reviews_per_user)

        fig, ax = plt.subplots()
        sns.barplot(
            x=user_categories.index,
            y=user_categories.values,
            ax=ax,
            palette="Blues_r",
            hue=user_categories.index,
        )
        ax.set_xlabel("User Category")
        ax.set_ylabel("Number of Users")
        plt.xticks(rotation=25)
        sns.despine()
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        st.pyplot(fig)
        plt.close(fig)  # Free memory
        st.markdown(
            """
            **User Categorization by Activity:**

            We observe that "occasional" users dominate, followed by a smaller core of regular and active users.
            "Super-active" users (>20 reviews) are rare but essential: they drive the platform and generate quality content.
            This typology allows us to adapt our community engagement strategy accordingly.
            """,
        )

    with col3:
        # Average rating per user
        st.subheader("Average rating per user")
        df_user_stats = compute_user_stats(df_interactions)
        fig, ax = plt.subplots()
        sns.scatterplot(
            data=df_user_stats.to_pandas(),
            x="nb_reviews",
            y="mean_rating",
            ax=ax,
        )
        ax.set_xlabel("Number of Reviews")
        ax.set_ylabel("Average Rating")
        sns.despine()
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        st.pyplot(fig)
        plt.close(fig)  # Free memory
        st.markdown(
            """
            This scatter plot illustrates the relationship between user activity (number of reviews) and their average rating.
            We observe that less active users tend to give lower ratings, while more active users show more variability in
            their ratings. This could suggest that occasional users are less generous or more critical, or only comment when
            they don't like a recipe. In contrast, frequent reviewers tend to give five-star ratings.

            We can also see some outliers with a very high number of ratings almost set to five stars—we suspect these to be bots.
            """,
        )
