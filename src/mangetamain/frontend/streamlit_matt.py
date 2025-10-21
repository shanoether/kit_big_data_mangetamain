import streamlit as st
import os
import time
from recipe_analyzer import RecipeAnalyzer

# Configuration de base
st.set_page_config(page_title="Analyse Recettes", layout="wide")
st.title("📊 Analyse des Recettes et Reviews")

# Chargement des données avec sablier
with st.spinner("Chargement des données en cours..."):
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "raw")
    PATH_RECIPE = os.path.join(DATA_DIR, "RAW_recipes.csv")
    PATH_INTERACTION = os.path.join(DATA_DIR, "RAW_interactions.csv")

    @st.cache_resource
    def get_analyzer():
        return RecipeAnalyzer(PATH_RECIPE, PATH_INTERACTION)

    analyzer = get_analyzer()
    time.sleep(0.5)  # Simulation de chargement

# Sidebar avec options d'affichage
st.sidebar.header("Paramètres d'analyse")

# Sliders pour les paramètres
year_range = st.sidebar.slider(
    "Période (années)",
    min_value=2000,
    max_value=2019,
    value=(2005, 2015)
)

#---------------------------------------------


ingredient_count = st.sidebar.slider(
    "Nombre d'ingrédients",
    min_value=10,
    max_value=35,
    value=20
)

review_count = st.sidebar.slider(
    "Nombre de recettes",
    min_value=20,
    max_value=500,
    value=100
)

freq_words = st.sidebar.slider(
    "Mots max dans WordClouds",
    min_value=30,
    max_value=200,
    value=100
)

# Boutons pour afficher/masquer les sections
st.sidebar.header("Affichage")
show_histogram = st.sidebar.checkbox("Histogramme", value=True)
show_ingredients = st.sidebar.checkbox("Top ingrédients", value=True)
show_wordclouds = st.sidebar.checkbox("WordClouds (6)", value=True)
show_comparisons = st.sidebar.checkbox("Comparaisons (3)", value=True)


#
# Fonction pour afficher les wordclouds avec sabliers
def display_wordclouds():
    st.header("🗣️ WordClouds (6 graphiques)")

    categories = [
        ("Recettes les plus commentées", None),
        ("Recettes mieux notées", "best"),
        ("Recettes moins bien notées", "worst")
    ]

    # Grille 2x3 pour les 6 wordclouds
    for i, (title, filter_type) in enumerate(categories):
        st.subheader(title)
        cols = st.columns(2)

        with cols[0]:
            with st.spinner(f"Génération WordCloud (Fréquence) pour {title}..."):
                recipe_ids = analyzer.get_top_recipe_ids(
                    n=review_count,
                    rating_filter=filter_type
                )
                reviews = analyzer.get_reviews_for_recipes(recipe_ids)
                fig = analyzer.plot_word_frequency(
                    reviews,
                    f"Fréquence - {title}",
                    freq_words
                )
                st.pyplot(fig)

        with cols[1]:
            with st.spinner(f"Génération WordCloud (TF-IDF) pour {title}..."):
                fig = analyzer.plot_tfidf(
                    reviews,
                    f"TF-IDF - {title}",
                    freq_words
                )
                st.pyplot(fig)

# Fonction pour afficher les comparaisons avec sabliers
def display_comparisons():
    st.header("🔄 Comparaisons Fréquence/TF-IDF (3 graphiques)")

    categories = [
        ("Recettes les plus commentées", None),
        ("Recettes mieux notées", "best"),
        ("Recettes moins bien notées", "worst")
    ]

    # Grille 1x3 pour les 3 comparaisons
    cols = st.columns(3)
    for i, (title, filter_type) in enumerate(categories):
        with cols[i]:
            with st.spinner(f"Comparaison pour {title}..."):
                recipe_ids = analyzer.get_top_recipe_ids(
                    n=review_count,
                    rating_filter=filter_type
                )
                reviews = analyzer.get_reviews_for_recipes(recipe_ids)
                fig = analyzer.compare_frequency_and_tfidf(
                    reviews,
                    f"Comparaison - {title}",
                    freq_words
                )
                st.pyplot(fig)

# Affichage principal
if show_histogram:
    with st.spinner("Génération de l'histogramme..."):
        st.header("📈 Contributions par période")
        fig = analyzer.plot_contributions_by_semester(*year_range)
        st.pyplot(fig)

if show_ingredients:
    with st.spinner("Calcul des ingrédients..."):
        st.header("🍳 Top ingrédients utilisés")
        fig = analyzer.plot_top_ingredients(ingredient_count)
        st.pyplot(fig)

if show_wordclouds:
    display_wordclouds()

if show_comparisons:
    display_comparisons()

# Informations supplémentaires
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Paramètres actuels:**")
st.sidebar.markdown(f"- Recettes analysées: {review_count}")
st.sidebar.markdown(f"- Mots par nuage: {freq_words}")
st.sidebar.markdown(f"- Période: {year_range[0]}-{year_range[1]}")
st.sidebar.markdown(f"- Ingrédients: {ingredient_count}")

st.markdown("---")
st.caption("© 2025 - Analyse de données culinaires")
