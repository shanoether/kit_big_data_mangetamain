"""Trends analysis page of the Streamlit app."""

import matplotlib.pyplot as plt
import polars as pl
import seaborn as sns
import streamlit as st

st.set_page_config(
    page_title="Trends",
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

st.title("📈 Trends")
st.markdown("""
            Temporal trends and popular recipe categories
            """)
st.markdown("""---""")


@st.cache_data(show_spinner="Computing trends...")  # type: ignore[misc]
def compute_yearly_trends(_df_interactions: pl.DataFrame) -> pl.DataFrame:
    """Compute average ratings per year (cached).

    Args:
        _df_interactions: DataFrame with interactions data

    Returns:
        DataFrame with year and mean_rating columns
    """
    df_interaction = _df_interactions.with_columns(
        pl.col("date").dt.year().alias("year"),
    )
    return (
        df_interaction.group_by("year")
        .agg(pl.col("rating").mean().alias("mean_rating"))
        .sort("year")
    )


@st.cache_data(show_spinner="Computing monthly trends...")  # type: ignore[misc]
def compute_monthly_trends(_df_interactions: pl.DataFrame) -> pl.DataFrame:
    """Compute number of reviews per month and year (cached).

    Args:
        _df_interactions: DataFrame with interactions data

    Returns:
        DataFrame with year, month, and nb_reviews columns
    """
    df_interaction = _df_interactions.with_columns(
        [
            pl.col("date").dt.year().alias("year"),
            pl.col("date").dt.month().alias("month"),
        ],
    )
    return (
        df_interaction.group_by(["year", "month"])
        .agg(pl.len().alias("nb_reviews"))
        .sort(["year", "month"])
    )


if "data_loaded" in st.session_state and st.session_state.data_loaded:
    df_interactions = st.session_state.df_interactions_nna

    col1, _, col2 = st.columns([1, 0.05, 1])
    # Evolution of average ratings
    with col1:
        st.markdown(
            '<h3 style="text-align:center;">Evolution of average ratings per year</h4>',
            unsafe_allow_html=True,
        )
        # st.subheader("Evolution of average ratings per year")
        mean_by_year = compute_yearly_trends(df_interactions)

        fig, ax = plt.subplots(figsize=(8, 5))
        sns.lineplot(
            data=mean_by_year,
            x="year",
            y="mean_rating",
            marker="o",
            ax=ax,
        )
        ax.set_ylim(0, 5)
        ax.grid()
        plt.xticks(range(2000, 2019, 3))
        sns.despine()
        plt.tight_layout(rect=[0, 0, 1, 0.95])

        st.pyplot(fig)
        plt.close(fig)  # Free memory

    # Number of reviews per month and year
    with col2:
        st.markdown(
            '<h3 style="text-align:center;">Number of reviews per month and year</h3>',
            unsafe_allow_html=True,
        )
        monthly_counts = compute_monthly_trends(df_interactions)

        fig, ax = plt.subplots(figsize=(8, 5))
        sns.lineplot(
            data=monthly_counts,
            x="month",
            y="nb_reviews",
            hue="year",
            marker="o",
            ax=ax,
        )
        plt.xticks(range(1, 13))
        sns.despine()
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        st.pyplot(fig)
        plt.close(fig)  # Free memory
