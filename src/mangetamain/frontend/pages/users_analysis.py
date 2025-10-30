"""Users Analysis for the Streamlit app."""

import matplotlib.pyplot as plt
import plotly.graph_objects as go
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
        Here we will apply clustering methods to group the users based on their reviewing activity. First we will work to find the optimal number of clusters (k) using both the elbow method and the silhouette score method. and then see how these cluster evolves in function time.
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
            <div style="text-align: justify;">
            <p>
            The analysis combines the elbow method and the silhouette method to determine the optimal number of clusters (k) in a MiniBatchKMeans clustering.
            The elbow method involves plotting the inertia (sum of squared distances of points to their cluster centers) as a function of k. The goal is to identify a point where the decrease in inertia slows significantly, forming an "elbow." This indicates that adding more clusters does not substantially improve the quality. However, this method can sometimes be ambiguous.
            The silhouette score method complements this analysis by measuring how well-separated and compact the clusters are, with values ranging from -1 to 1. A score close to 1 indicates well-defined clusters, a score near 0 indicates overlapping clusters, and a negative score indicates poor clustering.
            By combining these two criteria, a more robust choice of k is achieved. In practice, we prefer a k where the inertia begins to stabilize and the silhouette score is maximized. This ensures that the clusters are both compact and well-separated, making them easier to interpret and use later.
            For the silhouette method, the calculations were performed using *verb|sklearn.metrics.silhouette.score|*
            </p>
            </div>
            """,
        unsafe_allow_html=True,
    )

    # --- 1. Créer le DataFrame Polars ---
    # Thosev values were computed before hand because they require long processing time
    df_scores = pl.DataFrame(
        {
            "k": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            "inertie": [
                724608.3,
                565130.2,
                498131.1,
                481338.3,
                483306.3,
                446134.1,
                451036.6,
                452287.7,
                413176.4,
                430706.9,
            ],
            "silhouette": [
                0.6394,
                0.7443,
                0.6585,
                0.7304,
                0.6974,
                0.7785,
                0.7810,
                0.7258,
                0.7865,
                0.7492,
            ],
        }
    )

    # --- 2. Trouver automatiquement le meilleur k selon silhouette ---
    best_row = df_scores.sort("silhouette", descending=True).row(0)
    best_k, best_sil = best_row[0], best_row[2]

    # --- 3. Visualisation combinée avec Plotly ---
    fig = go.Figure()

    # Trace 1: Inertie (axe gauche)
    fig.add_trace(
        go.Scatter(
            x=df_scores["k"],
            y=df_scores["inertie"],
            mode="lines+markers",
            name="Inertie",
            line=dict(color="blue"),
            marker=dict(symbol="circle", size=8),
            yaxis="y",
        )
    )

    # Trace 2: Silhouette Score (axe droit)
    fig.add_trace(
        go.Scatter(
            x=df_scores["k"],
            y=df_scores["silhouette"],
            mode="lines+markers",
            name="Silhouette Score",
            line=dict(color="orange"),
            marker=dict(symbol="square", size=8),
            yaxis="y2",
        )
    )

    # Ligne verticale pour le meilleur k
    fig.add_vline(
        x=best_k,
        line_dash="dash",
        line_color="green",
        opacity=0.7,
        annotation_text=f"k={best_k}<br>score={best_sil:.3f}",
        annotation_position="top right",
        annotation=dict(font_color="green"),
    )

    # Configuration du layout avec deux axes y
    fig.update_layout(
        title="Méthodes du Coude et du Silhouette Score pour MiniBatchKMeans",
        xaxis=dict(
            title="Nombre de clusters (k)",
            showgrid=True,
            gridcolor="lightgray",
            griddash="dash",
        ),
        yaxis=dict(
            title="Inertie",
            tickfont=dict(color="blue"),
            showgrid=True,
            gridcolor="lightgray",
            griddash="dash",
        ),
        yaxis2=dict(
            title="Silhouette Score",
            tickfont=dict(color="orange"),
            overlaying="y",
            side="right",
        ),
        legend=dict(
            x=0.02,
            y=0.98,
            xanchor="left",
            yanchor="top",
            bgcolor="rgba(255, 255, 255, 0.8)",
        ),
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True)
