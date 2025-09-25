# create venv for the jupyter kernel
# run in vscode
# https://medium.com/@luismarcelobp/create-virtual-environments-with-uv-to-use-jupyter-notebooks-inside-vs-code-48f336023e7f

uv init --package                 # creates src/ and pyproject.toml
uv venv --python 3.12             # choose python version need python 3.10 to avoid tensorflow incompatibility
uv add --dev ruff mypy pytest black ipykernel jupyterlab ipython
uv sync

uv run ipython kernel install --user --name=venv-3.12-mangetamain --display-name "Python 3.12 (mangetamain)"
# adapt the dependencies in toml

# Useful kernel command

# See available kernels
uv run jupyter kernelspec list

# Delete old kernel if exists
uv run jupyter kernelspec uninstall python3