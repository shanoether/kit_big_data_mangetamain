# Environment Setup Playbook

This playbook covers environment setup, configuration, and troubleshooting for the Mangetamain project.

## Table of Contents
- [Initial Environment Setup](#initial-environment-setup)
- [Virtual Environment with UV](#virtual-environment-with-uv)
- [Jupyter Kernel Configuration](#jupyter-kernel-configuration)
- [Dependency Management](#dependency-management)
- [Troubleshooting](#troubleshooting)

---

## Initial Environment Setup

### Requirements
- Python 3.12 (required to avoid TensorFlow incompatibility)
- UV package manager
- VS Code (recommended)

### Create Project Structure

```bash
# Initialize project with package structure
uv init --package  # Creates src/ and pyproject.toml

# Create virtual environment with Python 3.12
uv venv --python 3.12
```

### Install Development Dependencies

```bash
# Add essential development tools
uv add --dev ruff mypy pytest black ipykernel jupyterlab ipython

# Sync all dependencies
uv sync
```

---

## Virtual Environment with UV

### Basic UV Commands

```bash
# Sync dependencies from pyproject.toml and lock file
uv sync

# Sync including development dependencies
uv sync --group dev

# Build distribution packages (wheel + sdist)
uv build
```

### Quality Assurance Tools

```bash
# Check code formatting issues
uv run ruff check .

# Auto-fix formatting errors
uv run ruff format .

# Type checking for consistency
uv run mypy .

# Run unit tests
uv run pytest
```

---

## Jupyter Kernel Configuration

### Install Jupyter Kernel for VS Code

Create a custom kernel for the project:

```bash
uv run ipython kernel install --user \
  --name=venv-3.12-mangetamain \
  --display-name "Python 3.12 (mangetamain)"
```

### Useful Kernel Management Commands

```bash
# List all available Jupyter kernels
uv run jupyter kernelspec list

# Remove old/unused kernel
uv run jupyter kernelspec uninstall python3
```

### Configuration Notes
- Adapt dependencies in `pyproject.toml` after kernel installation
- The kernel name `venv-3.12-mangetamain` should match your project structure
- Reference: [Create Virtual Environments with UV for Jupyter in VS Code](https://medium.com/@luismarcelobp/create-virtual-environments-with-uv-to-use-jupyter-notebooks-inside-vs-code-48f336023e7f)

---

## Dependency Management

### Python Version Configuration

Edit `pyproject.toml`:

```toml
[tool.uv]
python = "3.12.*"
```

### Standard Dependencies

```bash
# Add runtime dependencies
uv add package-name

# Add development-only dependencies
uv add --dev package-name

# Remove dependencies
uv remove package-name
```

---

## Troubleshooting

### PyArrow Installation Issues

If you encounter PyArrow compatibility issues:

**Problem**: PyArrow binary build failures or version conflicts

**Solution**:

1. **Modify `pyproject.toml`**:
   ```toml
   [tool.uv]
   python = "3.12.*"
   ```

2. **Force binary-only installation**:
   ```bash
   # Set environment variable to use pre-built binaries only
   export UV_PIP_ONLY_BINARY=":all:"
   # Alternative:
   export PIP_ONLY_BINARY=":all:"
   ```

3. **Install compatible PyArrow version**:
   ```bash
   # Recreate virtual environment
   uv venv --recreate

   # Install PyArrow with version constraint
   uv add "pyarrow>=16,<18" --no-sync

   # Sync all dependencies
   uv sync
   ```

### Common Environment Issues

#### Issue: Dependencies Not Found After Installation

**Solution**:
```bash
# Clear cache and reinstall
uv cache clean
uv sync --reinstall
```

#### Issue: Virtual Environment Not Activated

**Solution**:
```bash
# Check if virtual environment exists
ls .venv

# Activate manually (if needed)
source .venv/bin/activate  # Unix/macOS
# or
.venv\Scripts\activate  # Windows
```

#### Issue: Python Version Mismatch

**Solution**:
```bash
# Recreate venv with specific Python version
uv venv --recreate --python 3.12

# Verify Python version
uv run python --version
```

#### Issue: Jupyter Kernel Not Appearing in VS Code

**Solution**:
```bash
# Reinstall kernel
uv run jupyter kernelspec uninstall venv-3.12-mangetamain
uv run ipython kernel install --user \
  --name=venv-3.12-mangetamain \
  --display-name "Python 3.12 (mangetamain)"

# Restart VS Code
# Select the correct kernel in notebook interface
```

### Environment Variables

When working with Google Cloud or other services requiring credentials:

```bash
# Load environment variables from .env file
set -a && source .env && set +a
```

---

## Best Practices

1. **Always sync after modifying dependencies**:
   ```bash
   uv sync
   ```

2. **Use specific Python versions** to avoid compatibility issues

3. **Keep development dependencies separate** using `--dev` flag

4. **Regularly update dependencies**:
   ```bash
   uv sync --upgrade
   ```

5. **Use virtual environments** to isolate project dependencies

6. **Document custom requirements** in `pyproject.toml` comments
