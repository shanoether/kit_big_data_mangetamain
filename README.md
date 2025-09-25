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

## How to contribute

Work on separate notebook or use branch in git: 
1. Branch to dev: `git checkout -b <dev-branch-name>`-
2. Commit your (multiple changes) 
```bash
git add .
git commit -m "My feature work"
git push -u origin dev
```
- When changes accpeted by team and reviewed, merge: 
```bash
git checkout main
git pull origin main        # update main with latest from remote
git merge dev               # merge dev into main
git add .
git commit -m "Merge with dev for my feature"
git push origin main        # publish merged main
```
- Then go back to your dev branch: 
```bash
git checkout dev
git pull origin main   # or: git merge main
```

## Introduction

## Conclusion
