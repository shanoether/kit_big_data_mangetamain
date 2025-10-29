"""Users Analysis for the Streamlit app."""

import matplotlib.pyplot as plt
import polars as pl
import seaborn as sns
import streamlit as st

st.set_page_config(
    page_title="Users Analysis",
    page_icon="👤",
    layout="centered",
    initial_sidebar_state="expanded",
)


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


st.title("Users Analysis")

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
    st.pyplot(fig)
    plt.close(fig)  # Free memory

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
    st.pyplot(fig)
    plt.close(fig)  # Free memory
