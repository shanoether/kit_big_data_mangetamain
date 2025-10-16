import streamlit as st
import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Trends",
    page_icon="⏳",
    layout="centered",    
    initial_sidebar_state="expanded"
)
st.title("Trends")

if 'data_loaded' in st.session_state and st.session_state.data_loaded:
    df_interactions = st.session_state.df_interactions

    # Parsing des dates
    df_interaction = df_interactions.with_columns([
        pl.col("date").alias("date_parsed")
    ])
    df_interaction = df_interaction.with_columns([
        pl.col("date_parsed").dt.year().alias("year"),
        pl.col("date_parsed").dt.month().alias("month")
    ])

    # Évolution des notes moyennes
    st.subheader("Évolution des notes moyennes par année")
    mean_by_year = (
        df_interaction
        .group_by("year")
        .agg(pl.col("rating").mean().alias("mean_rating"))
        .sort("year")
    )
    fig, ax = plt.subplots()
    sns.lineplot(data=mean_by_year.to_pandas(), x="year", y="mean_rating", marker="o", ax=ax)
    st.pyplot(fig)

    # Nombre de reviews par mois et année
    st.subheader("Nombre de reviews par mois et année")
    monthly_counts = (
        df_interaction
        .group_by(["year", "month"])
        .agg(pl.count().alias("nb_reviews"))
        .sort(["year", "month"])
    )
    fig, ax = plt.subplots()
    sns.lineplot(data=monthly_counts.to_pandas(), x="month", y="nb_reviews", hue="year", marker="o", ax=ax)
    plt.xticks(range(1,13))
    st.pyplot(fig)
