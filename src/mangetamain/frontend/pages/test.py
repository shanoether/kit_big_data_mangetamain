import streamlit as st
from mangetamain.frontend.core.utils import load_csv

st.title("Test Page")

df = load_csv("data/RAW_interactions.csv")
st.write(df.head())