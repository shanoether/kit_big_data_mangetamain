# 🍽️ Kit Big Data: Mangetamain

Mangetamain is a **Streamlit web application** designed for **data analysis and visualization of cooking recipes and user interactions** based on the [Food.com Kaggle dataset](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions/data).  
It provides an interactive interface for exploring recipes, understanding user preferences, and identifying food trends using big data tools and visualization techniques.

---

## 🚀 Features

- **Recipe analysis**: Extract and visualize key recipe metrics (ingredients, steps, time, etc.)
- **User interaction insights**: Analyze user ratings, reviews, and behavioral trends
- **Data cleaning and preprocessing**: Automatic data processing into parquet format
- **Interactive dashboards** built with **Streamlit**
- **Modular architecture** separating backend, frontend, and utilities
- **Docker support** for easy deployment

---

## 🧠 Usage

Once the app is running, you can:
- Explore recipes and user interactions through interactive dashboards.
- Filter recipes by time, rating, or ingredients.
- Visualize rating distributions and popularity trends.
- To do this, you can access multiple analytical pages:
   - Overview
   - Recipe Analysis
   - User Analysis
   - Trends
   - Ratings Dashboard

---

## 🧰 Installation

### 1. Clone the repository

```bash
git clone https://github.com/shanoether/kit_big_data_mangetamain.git
cd kit_big_data_mangetamain
```
---

### 2. Setup the environment (recommended: UV)

```bash
uv venv --python 3.12
uv sync --group dev 
uv run ipython kernel install --user --name=venv-3.12-mangetamain --display-name "Python 3.12 (mangetamain)"
```
---

## 📦 Data Setup

Download the dataset from Kaggle.
Place the following files in the folder data/raw/:
- RAW_interactions.csv
- RAW_recipes.csv  
Processed versions (.parquet) will be generated automatically in data/processed/.

---

## ▶️ Execution

To run the Streamlit application locally:
```bash
uv run streamlit run src/mangetamain/streamlit_ui.py
```
Then open your browser at:

http://localhost:8501

---

## ☁️ Deployment

Using Docker

### 1. Build the Docker image

```bash 
docker build -t mangetamain-app .
```
### 2. Run the container

```bash 
docker run -p 8501:8501 mangetamain-app
```
---
## 🧪 Tests

The project includes unit tests to ensure code quality and reliability of features.  
The tests mainly cover:

- **Backend**: data processing, cleaning, transformation, and generation of `.parquet` files.  
- **Utils**: utility functions like the logger and other helpers.  
- **Frontend**: (if applicable) certain interactive features and Streamlit displays.

### 1. Run all tests

To run all unit tests in the project:

```bash 
uv run pytest tests/unit/
```

### 2. Run a specify test
For example, to test only the data_processor module:

```bash 
uv run pytest tests/unit/mangetamain/backend/test_data_processor.py
```
---

## 🧱 Project Structure

kit_big_data_mangetamain/
├── data/
│   ├── processed/
│   │   ├── processed_interactions.parquet
│   │   └── processed_recipes.parquet
│   └── raw/
│       ├── RAW_interactions.csv
│       └── RAW_recipes.csv
├── docs/
│   ├── git-start.md
│   ├── uml_big_data.jpeg
│   ├── uml_usecase.png
│   └── Projet mangetamain.pdf
├── src/
│   └── mangetamain/
│       ├── backend/
│       │   ├── data_processor.py
│       │   └── helper.py
│       ├── frontend/
│       │   └── pages/
│       │       ├── dashboard.py
│       │       ├── overview.py
│       │       ├── recipe_analysis.py
│       │       ├── trends.py
│       │       └── user_analysis.py
│       ├── utils/
│       │   └── logger.py
│       └── streamlit_ui.py
├── tests/
│   └── unit/
│       └── mangetamain/
│           ├── backend/
│           │   └── test_data_processor.py
│           └── utils/
│               └── test_logger.py
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── README.md

## 🧑‍💻 Contributing 

Work on a separate branch or notebook:
```bash 
git checkout -b dev/<feature-name>
```

Commit your changes:

```bash 
git add . 
git commit -m "My feature work" 
git push -u origin dev/<feature-name>
``` 

Merge after review:

```bash 
git checkout dev 
git pull origin dev
git merge dev/<feature-name>
git push origin dev
```
---

## 🌱 Future Improvements

Planned or possible enhancements:

- Recommendation engine based on user taste
- Recipe clustering for similarity analysis
- Export dashboards to PDF
- Add more interactive visualizations

---
## 📚 Credits

Dataset: Food.com Recipes and User Interactions (Kaggle)
Authors : 