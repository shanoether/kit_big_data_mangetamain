# Mangetamain, Garde l'Autre Pour Demain - A Food Data Visualiaation Tool

## Introduction

*Mangetamin* is a leader of the B2C client recommendation thanks to its massive data analytics methodology. Today it will share with the all world its best insights so that everybody at home can cook the best meal! How? Through a webapp visualization platform where we can analyze and see why some recipes are so delicious... or not! Go to [](http://34.1.14.43:8501/) to learn more about how our recipes are rated, what are the trends and how our users behaves on our website.


## How to Run This Project

**Run locally**
You can run locally the project by following those steps
1. Install [UV](https://docs.astral.sh/uv/getting-started/installation/)
2. Clone the project: `git clone https://
3. Set-up the environment: `uv sync`
4. Download the data from [kaggle](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions/data?select=RAW_interactions.csv): `RAW_interactions.zip.csv` and `RAW_recipes.zip.csv` and save them in /data/raw
5. Run the pre-processing tool: `uv run python src/mangetamain/backend/data_processor.py`
6. When the pre-processing is done, you can launch locally teh streamlit app with: `uv run streamlit run src/mangetamain/streamlit_ui.py`
7. Then visit http://http://localhost:8501 to see your web app

**Docker**

Alternatively you can also build docker image by using docker compose:
`docker-compose -f docker-compose-local.yml up`
This will build locally a docker image, spaw a first container that will run the preprocessing and saving the preprocessed files on disk and then launch the webapp within a container. To stop the webapp run:

`docker-compose -f docker-compose-local.yml down`


##

## Structure of the project

@copilot fill that in with directory struture and most import parts

##
