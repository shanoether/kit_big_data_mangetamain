"""Trends analysis page of the Streamlit webapp."""

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
st.markdown(
    """
    <div style="text-align: justify;">
    <p>
    This page analyzes trends in user ratings and review activity over time on the Mangetamain platform.
    We will examine how average ratings have evolved year by year,
    as well as the monthly distribution of reviews to identify any seasonal patterns or shifts in user engagement.
    </p>
    </div>""",
    unsafe_allow_html=True,
)
st.markdown("""---""")


@st.cache_data(show_spinner="Computing trends...")  # type: ignore[misc]
def compute_yearly_trends(
    _df_interactions: pl.DataFrame,
) -> pl.DataFrame:  # ignorore[misc]
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
def compute_monthly_trends(
    _df_interactions: pl.DataFrame,
) -> pl.DataFrame:  # ignore[misc]
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
        st.markdown(
            """
            <div style="text-align: justify;">
            <p>

        **Change in Average Score per Year:**

        The average recipe rating rose steadily between 2000 and 2006, from around 3.9 to 4.6, reflecting a very
        positive initial phase in which users generously rated the most popular recipes. From 2007 onwards, the trend
        reversed: ratings gradually declined to around 3.4 in 2017, which may reflect a diversification of content,
        a broader audience, or a more critical assessment of recipes over time.
        """,
            unsafe_allow_html=True,
        )

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
        st.markdown(
            """
            <div style="text-align: justify;">
            <p>

        **Number of Reviews per Month and per Year:**

        The number of reviews does not show any marked seasonal peaks, suggesting relatively stable activity throughout
        the year. However, there was a gradual decline in the volume of reviews between 2002 and 2017, indicating a
        decline in community engagement over time - possibly linked to a loss of interest in the platform or competition
        from other recipe - sharing sites.
        </p>
        </div>
        """,
            unsafe_allow_html=True,
        )
