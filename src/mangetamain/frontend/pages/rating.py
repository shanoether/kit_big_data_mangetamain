import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Rating Analysis",
    page_icon="🍳",
    
    initial_sidebar_state="expanded"
)
st.title("Rating")

if 'data_loaded' in st.session_state and st.session_state.data_loaded:
    df = st.session_state.df
        
    st.subheader("📊 Data Preview")
    
    # show first 10 rows of dataframe
    st.write("**Data from session_state:**")
    st.dataframe(df.head(10))
    st.write(f"Shape: {df.shape}")

    # draw histogram of ratings
    st.subheader("📈 Rating Distribution")
    st.bar_chart(df['rating'].value_counts())

    # draw boxplot of ratings
    st.subheader("📊 Rating Boxplot")

    fig, ax = plt.subplots()
    ax.boxplot(df['rating'].dropna(), vert=True)
    ax.set_title("Boxplot of Ratings")
    ax.set_ylabel("Values")

    # Show in Streamlit
    st.pyplot(fig)
            
else:
    st.error("❌ Data not loaded properly. Please refresh the page.")

