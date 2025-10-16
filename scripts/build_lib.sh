uv pip install dist/*.whl           # installs locally to verify
python -c "import mypkg; print(mypkg.__name__)"
pipx run twine check dist/*         # metadata check (optional but recommended)

