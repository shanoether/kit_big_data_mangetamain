# Kit Big Data: Mangetamain
``
## How to run this project

1. Set up the environment (I recommend to use UV and that's what I did)
   1. Install uv
   2. Spin up the environment
        ```bash
        uv venv --python 3.12         
        uv sync
        uv add --dev ruff mypy pytest black ipykernel jupyterlab ipython
        uv run ipython kernel install --user --name=venv-3.12-mangetamain --display-name "Python 3.12 (mangetamain)"
        ```
    3. Select the right python kernel for jupyternotebook (reload windows if necessary from command palet)
2. Donwload data
   1. The project data can be found in [kaggle](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions/data?select=RAW_interactions.csv)
   2. Download the data called RAW_interactions.zip.csv and RAW_recipes.zip.csv and put them in the folder `data/raw/`
   3. 
      1. 
`


## How to contribute

Work on separate notebook or use branch in git: 
1. Branch to dev: `git checkout -b <dev-branch-name>`-
2. Commit your (multiple changes) 
```bash
git add .
git commit -m "My feature work"
git push -u origin dev/myfeature
```
- When changes accpeted by team and reviewed, merge with dev: 
```bash
git checkout dev
git pull origin dev        # update main with latest from remote
git merge dev/myfeature               # merge dev into main
git add .
git commit -m "Merge with dev for my feature"
git push origin dev        # publish merged main
```
- Then go back to your dev branch: 
```bash
git checkout dev/myfeature
git pull origin dev   # or: git merge main
```

## Introduction

## Conclusion
