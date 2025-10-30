"""Users Analysis for the Streamlit app."""

import matplotlib.pyplot as plt
import plotly.express as px
import polars as pl
import seaborn as sns
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

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

icon = "👉"

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


@st.cache_data(show_spinner="Computing clusters...")  # type: ignore[misc]
def compute_cluster(
    _df_user: pl.DataFrame, _df_interactions: pl.DataFrame, n_clusters: int
) -> pl.DataFrame:
    """Cluster users based on their activity (number of reviews and mean rating).

    Args:
        _df_user: DataFrame with user statistics
        _df_interactions: DataFrame with interactions data
        n_clusters: Number of clusters to form

    Returns:
        DataFrame with user_id and cluster labels
    """
    features = ["nb_reviews", "mean_rating", "std_rating", "review_length", "mean_time"]
    _df_user = _df_user.drop_nulls()
    pd_user = _df_user[features].to_pandas()
    scaler = StandardScaler()
    
    pd_user_scaled = scaler.fit_transform(pd_user)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster = kmeans.fit_predict(pd_user_scaled)
    
    pd_user["cluster"] = cluster.astype(str)
    _df_user = _df_user.with_columns(pl.Series("cluster", cluster))
    df_interactions_cluster = _df_interactions.join(_df_user, on="user_id", how="inner")
    
    df_time = (
        df_interactions_cluster.with_columns(
            pl.col("date").dt.truncate("1mo").alias("month")
        )
        .group_by(["month", "cluster"])
        .agg(pl.len().alias("n_interactions"))
        .sort("month")
    )

    return pd_user, df_interactions_cluster, df_time.to_pandas()

st.markdown(
    """
    <div style="text-align: justify;">
    <p>
    This page provides an analysis of user behavior on the Mangetamain platform.
    We will explore the distribution of reviews per user,
    categorize users based on their activity levels,
    and examine the relationship between user activity and average ratings.
    </p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("""---""")


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
    st.header(f"{icon} Distribution of reviews per user")
    col1, space, col2 = st.columns([2, 0.05, 1.5])
    with col1:
        st.markdown(
            """
            <div style="text-align: justify;">
            <p>
            This graph shows a highly unbalanced distribution: the majority of recipes have only a small number of reviews,
            while a minority attract a huge number of comments. This illustrates a "long tail" phenomenon where a handful
            of very popular recipes generate a large part of the activity, while most remain largely unrated.
            On a logarithmic scale, this inequality becomes more visible.

            The majority of users leave only one review, indicating many are occasional users. In contrast, a minority of
            very active users produce a large volume of comments. This reflects a two-tiered community: many passive
            consumers and a few loyal contributors. We observe that someone has made approximately 7,500 reviews—likely
            either a bot or an enthusiast.
            </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
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

    col1, space, col2 = st.columns([1, 0.05, 1])

    with col1:
        st.header(f"{icon} User categorization")

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
        # **User Categorization by Activity:**
        st.markdown(
            """
            <div style="text-align: justify;">
            <p>
            We observe that "occasional" users dominate, followed by a smaller core of regular and active users.
            "Super-active" users (>20 reviews) are rare but essential: they drive the platform and generate quality content.
            This typology allows us to adapt our community engagement strategy accordingly.
            </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        # Average rating per user
        st.header(f"{icon} Average rating per user")
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
            <div style="text-align: justify;">
            <p>
            This scatter plot illustrates the relationship between user activity (number of reviews) and their average rating.
            We observe that less active users tend to give lower ratings, while more active users show more variability in
            their ratings. This could suggest that occasional users are less generous or more critical, or only comment when
            they don't like a recipe. In contrast, frequent reviewers tend to give five-star ratings.

            We can also see some outliers with a very high number of ratings almost set to five stars—we suspect these to be bots.
            </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.header(f"{icon} Clustering of users based on their activity")
    st.markdown(
        """
        <div style="text-align: justify;">
        <p>
        Here we will apply clustering methods to group the users based on their reviewing activity. We will consider the following parameters for the clustering:
        - Average rating
        - Standard deviation of the ratings
        - Number of reviews
        - Average length of the reviews
        - Average time of the recipe that has been reviewed
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("You can select below the number of clusters")
    n_clusters = st.slider("number of clusters", 2, 10, 7)

    pd_user, df_interactions_cluster, pd_date = compute_cluster(
        st.session_state.df_user,
        st.session_state.df_interactions,
        n_clusters=n_clusters,
    )

    # Double scatter plot

    st.subheader(f"{icon} Clusters Characteristics")
    col1, space, col2 = st.columns([1, 0.05, 1])
    with col1, st.spinner("Generating Plots"):
            fig = px.histogram(
                pd_user,  # convert from Polars
                x="cluster",
                nbins=n_clusters,  # one bin per cluster
                title="Number of user per cluster",
                labels={"cluster": "Cluster", "count": "Number of users"},
            )
            st.plotly_chart(fig, use_container_width=True)

            fig = px.scatter(
                pd_user,
                x="nb_reviews",
                y="mean_rating",
                color="cluster",
                opacity=0.7,
                color_discrete_sequence=px.colors.qualitative.Bold,
                title="Number of review vs mean rating per uer",
                labels={
                    "nb_reviews": "Number of review",
                    "mean_rating": "Mean rating",
                    "cluster": "Cluster",
                },
            )
            fig.update_traces(marker={"size": 4})
            st.plotly_chart(fig, use_container_width=True)

    with col2, st.spinner("Generating Scatterplots"):
        # review lenght vs mean rating
        fig = px.scatter(
            pd_user,
            x="review_length",
            y="mean_rating",
            color="cluster",
            opacity=0.7,
            color_discrete_sequence=px.colors.qualitative.Bold,
            title="Length of the review vs mean rating per user",
            labels={
                "nb_reviews": "Number of review",
                "review_length": "Mean number of words per review",
                "cluster": "Cluster",
            },
        )
        fig.update_traces(marker={"size": 4})
        st.plotly_chart(fig, use_container_width=True)

    
        # nb review vs review length
        fig = px.scatter(
            pd_user,
            x="nb_reviews",
            y="review_length",
            color="cluster",
            opacity=0.7,
            color_discrete_sequence=px.colors.qualitative.Vivid,
            title="Number of review vs review length per user",
            labels={
                "nb_reviews": "Number of review",
                "review_length": "Mean number of words per review",
                "cluster": "Cluster",
            },
        )
        fig.update_traces(marker={"size": 4})
        st.plotly_chart(fig, use_container_width=True)

    st.subheader(f"{icon} Clusters Evolution Over Time")

    with st.spinner("Generating Time Evolution Plot"):
        fig = px.line(
            pd_date,
            x="month",
            y="n_interactions",
            color="cluster",
            title="Interactions per cluster over time",
            labels={
                "month": "date (per month)",
                "n_interactions": "Number of review per cluster",
                "cluster": "Cluster",
            },
        )
        fig.update_xaxes(type="date")
        st.plotly_chart(fig, use_container_width=True)
