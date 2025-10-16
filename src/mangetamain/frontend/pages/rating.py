import streamlit as st
import pandas as pd
import polars as pl
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="Rating Analysis",
    page_icon="🍳",
    layout="centered",    
    initial_sidebar_state="expanded"
)
st.title("Rating")

if 'data_loaded' in st.session_state and st.session_state.data_loaded:
    df_interactions = st.session_state.df_interactions
        
    st.subheader("📊 Data Preview")
    
    # show first 10 rows of dataframe
    st.write("**Data from session_state:**")
    st.dataframe(df_interactions.head(10))
    st.write(f"Shape: {df_interactions.shape}")

    # draw histogram of ratings
    st.subheader("📈 Rating Distribution")
    st.bar_chart(df_interactions['rating'].value_counts())

    # draw boxplot of ratings
    st.subheader("📊 Rating Boxplot")

    fig, ax = plt.subplots()
    ax.boxplot(df_interactions['rating'].drop_nans(), vert=True)
    ax.set_title("Boxplot of Ratings")
    ax.set_ylabel("Values")


    # Show in Streamlit
    st.pyplot(fig)

    # Visualisation distribution des recettes par review
    reviews_per_recipe = reviews_per_recipe = (df_interactions.group_by("recipe_id").agg(pl.count().alias("review_count")))
    fig, ax = plt.subplots()
    sns.histplot(reviews_per_recipe, bins=30, log_scale=(False, True), ax=ax)  # échelle log pour mieux visualiser
    ax.set_title("Distribution du nombre de reviews par recette")
    ax.set_xlabel("Nombre de reviews")
    ax.set_ylabel("Nombre de recettes (échelle log)")
    st.pyplot(fig)

    st.header("Time Evolution of Ratings")
    st.markdown(
        """
            This section shows how ratings have evolved over time.
            Use the slider below to filter by year range.
            """,
    )

    min_year = int(df_interactions.select("year").min()[0, 0])
    max_year = int(df_interactions.select("year").max()[0, 0])

    # Streamlit slider for year selection
    year_range = st.slider(
        "Select year range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1,
    )

    # Filter DataFrame based on slider
    filtered_interactions = df_interactions.filter(
        (pl.col("year") >= year_range[0]) & (pl.col("year") <= year_range[1]),
    )

    # Number of rating by year
    fig_year, ax_year = plt.subplots()
    sns.histplot(data=filtered_interactions, x="year", discrete=True, bins=18)
    sns.despine()
    ax_year.set_title("Number of ratings by year")
    ax_year.set_xlabel("Year")
    ax_year.set_ylabel("Count")
    st.pyplot(fig_year)

    # Time evolution of ratings (filtered)
    fig_evolution_slider, ax_evolution_slider = plt.subplots()
    pa_filtered_df_interaction = filtered_interactions.select(
        ["year", "rating"],
    ).to_pandas()
    pa_filtered_df_interaction["year"] = pa_filtered_df_interaction["year"].astype(
        "category",
    )
    sns.histplot(
        data=pa_filtered_df_interaction,
        x="year",
        hue="rating",
        discrete=True,
    )
    sns.despine()
    ax_evolution_slider.set_title("Time evolution of ratings")
    ax_evolution_slider.set_xlabel("Year")
    ax_evolution_slider.set_ylabel("Count by rating")
    st.pyplot(fig_evolution_slider)
            
else:
    st.error("❌ Data not loaded properly. Please refresh the page.")

