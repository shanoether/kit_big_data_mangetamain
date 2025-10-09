import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import date
import streamlit as st
from mangetamain.frontend.core.utils import load_csv

@st.cache_data
def load_data():
    df_interaction = pd.read_csv("data/RAW_interactions.csv")
    df_recipe = pd.read_csv("data/RAW_recipes.csv")
    return df_interaction, df_recipe

st.title("Test Page")

df_interaction, df_recipe = load_data()
st.write(df_interaction.head())
