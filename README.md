# 🍽️ Mangetamain, Garde l'Autre Pour Demain

> *"Eat this one, save the other for tomorrow!"*

**Mangetamain** is a leader in B2C recipe recommendations powered by massive data analytics. We're sharing our best insights with the world through an interactive web platform where everyone can discover what makes recipes delicious... or not!
🌐 **[Visit Our Live Application](http://34.1.14.43:8501/)**

This **Streamlit web application** provides comprehensive **data analysis and visualization of cooking recipes and user interactions** based on the [Food.com Kaggle dataset](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions/data). Explore how recipes are rated, discover food trends, and understand user behavior through interactive dashboards powered by big data tools and advanced visualization techniques.

---

## 🚀 Features

- **📊 Recipe Analysis**: Extract and visualize key recipe metrics (ingredients, steps, cooking time, nutritional info)
- **👥 User Interaction Insights**: Analyze user ratings, reviews, and behavioral patterns
- **🔄 Automated Data Processing**: Efficient data cleaning and transformation into parquet format
- **📈 Interactive Dashboards**: Built with **Streamlit** for real-time data exploration
- **🎨 Advanced NLP Visualizations**:
  - Word clouds (frequency-based and TF-IDF)
  - Polar plots for ingredient analysis
  - Venn diagrams for method comparison
- **🏗️ Modular Architecture**: Clean separation of backend, frontend, and utilities
- **🐳 Docker Support**: Containerized deployment for easy scaling
- **⚡ High Performance**: Leverages Polars for 10x faster DataFrame operations

---

## 🧠 Usage

Once the application is running, you can access multiple analytical pages:

### 📱 Available Dashboards

1. **Overview** - High-level statistics and key metrics
2. **Recipe Analysis** - Deep dive into recipe characteristics and ingredients
3. **User Analysis** - User behavior patterns and engagement metrics
4. **Trends** - Temporal trends and popular recipe categories
5. **Ratings Dashboard** - Rating distributions and popularity analysis

### 🎯 Key Capabilities

- Filter recipes by preparation time, rating, or specific ingredients
- Visualize rating distributions and popularity trends over time
- Explore word clouds of recipe reviews and ingredient frequencies
- Compare different NLP analysis methods (frequency vs. TF-IDF)
- Interactive polar plots for ingredient category analysis

---

## 🛠️ Installation

### Prerequisites

- Python 3.12+
- [UV](https://docs.astral.sh/uv/) package manager
- Docker (optional, for containerized deployment)

### 📦 Option 1: Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/shanoether/kit_big_data_mangetamain.git
   cd kit_big_data_mangetamain
   ```

2. **Set up the environment**
   ```bash
   # Install dependencies
   uv sync

   # Install development dependencies (optional)
   uv sync --group dev
   ```

3. **Download spaCy language model**
   ```bash
   uv run hatch run dev:download-spacy
   ```

4. **Download the dataset**

   Download from [Kaggle Food.com dataset](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions/data):
   - `RAW_interactions.csv`
   - `RAW_recipes.csv`

   Place both files in `/data/raw/`

5. **Run data preprocessing**
   ```bash
   uv run python src/mangetamain/backend/data_processor.py
   ```

   This will generate processed `.parquet` and `.pkl` files in `data/processed/`

6. **Launch the Streamlit application**
   ```bash
   uv run streamlit run src/mangetamain/streamlit_ui.py
   ```

7. **Access the application**

   Open your browser at: `http://localhost:8501`

### 🐳 Option 2: Docker Installation

Build and run using Docker Compose:

```bash
# Build and start all services
docker-compose -f docker-compose-local.yml up

# Access the application at http://localhost:8501

# Stop the services
docker-compose -f docker-compose-local.yml down
```

This will:
1. Build the Docker image locally
2. Spawn a preprocessing container to process the data
3. Launch the Streamlit webapp in a container

---

## 📁 Project Structure

```
kit_big_data_mangetamain/
├── 📂 .github/
│   └── workflows/
│       └── deploy.yml              # CI/CD pipeline for automated deployment
├── 📂 config/                       # Configuration files
├── 📂 data/
│   ├── processed/                   # Processed data (.parquet, .pkl)
│   │   ├── processed_interactions.parquet
│   │   ├── processed_recipes.parquet
│   │   └── recipe_analyzer.pkl
│   └── raw/                         # Raw CSV data from Kaggle
│       ├── RAW_interactions.csv
│       └── RAW_recipes.csv
├── 📂 docs/                         # MkDocs documentation and playbooks
│   ├── index.md
│   ├── playbook-env.md             # Environment setup guide
│   ├── playbook-precommit.md       # Pre-commit workflow guide
│   ├── playbook-troubleshooting.md # Troubleshooting tips
│   ├── playbook-deployment-gcloud.md # GCP deployment guide
│   └── reference/                   # Auto-generated API docs
├── 📂 issue_template/               # GitHub issue templates
│   ├── bug_report.md
│   └── feature_request.md
├── 📂 logs/                         # Application logs
│   └── app/
├── 📂 notebook/                     # Jupyter notebooks for exploration
├── 📂 scripts/                      # Utility scripts
│   ├── pre-commit.sh               # Pre-commit checks
│   ├── build_docker.sh             # Docker build script
│   └── gloud-setup.sh              # GCP setup script
├── 📂 src/mangetamain/              # Main application code
│   ├── __init__.py
│   ├── streamlit_ui.py             # Main Streamlit application
│   ├── 📂 backend/
│   │   ├── data_processor.py       # ETL pipeline (DataProcessor class)
│   │   ├── recipe_analyzer.py      # NLP analysis (RecipeAnalyzer class)
│   │   └── helper.py               # Helper functions
│   ├── 📂 frontend/pages/          # Streamlit page modules
│   │   ├── dashboard.py            # Ratings dashboard
│   │   ├── overview.py             # Overview page
│   │   ├── recipes_analysis.py     # Recipe analysis page
│   │   ├── trends.py               # Trends page
│   │   └── users_analysis.py       # User analysis page
│   └── 📂 utils/
│       ├── logger.py               # Custom logging utility
│       └── helper.py               # General utilities
├── 📂 tests/                        # Test suite
│   └── unit/
│       └── mangetamain/
│           ├── backend/
│           │   ├── test_data_processor.py
│           │   ├── test_recipe_analyzer.py
│           │   └── test_helper.py
│           ├── utils/
│           │   └── test_logger.py
│           └── test_streamlit_ui.py
├── 📄 .pre-commit-config.yaml       # Pre-commit hooks configuration
├── 📄 docker-compose.yml            # Production Docker Compose
├── 📄 docker-compose-local.yml      # Local Docker Compose
├── 📄 Dockerfile                    # Multi-stage Docker build
├── 📄 mkdocs.yml                    # MkDocs configuration
├── 📄 pyproject.toml                # Project metadata & dependencies
└── 📄 README.md                     # This file
```

---

## 💻 Development Functionalities

### 🎯 Object-Oriented Programming (OOP)

The project follows **OOP best practices** with a clean, modular architecture. However the object oriented approach is very basic as `Streamlit`implements its onw logic and is not made to be run into different classes.

#### Core Classes

1. **`DataProcessor`** (`src/mangetamain/backend/data_processor.py`)
   - **Purpose**: ETL pipeline for data cleaning and transformation
   - **Key Methods**:
     - `load_data()`: Load and validate raw CSV/ZIP files
     - `drop_na()`: Remove rows with missing or unrealistic values
     - `split_minutes()`: Categorize recipes by cooking time
     - `merge_data()`: Join interactions with recipe metadata
     - `save_data()`: Export processed data to Parquet format
   - **Features**: Type hints, comprehensive docstrings, error handling

2. **`RecipeAnalyzer`** (`src/mangetamain/backend/recipe_analyzer.py`)
   - **Purpose**: NLP analysis and visualization of recipe data
   - **Key Methods**:
     - `preprocess_text()`: Batch spaCy processing for 5-10x performance
     - `frequency_wordcloud()`: Generate frequency-based word clouds
     - `tfidf_wordcloud()`: Generate TF-IDF weighted word clouds
     - `compare_frequency_and_tfidf()`: Venn diagram comparison
     - `plot_top_ingredients()`: Polar plots for ingredient analysis
   - **Features**: LRU caching, figure memoization, streaming support
   - **Serialization**: Supports `save()` and `load()` for pickle persistence

3. **`BaseLogger`** (`src/mangetamain/utils/logger.py`)
   - **Purpose**: Centralized logging with colored console output
   - **Features**:
     - Rotating file handlers (5MB max, 3 backups)
     - ANSI color codes for different log levels
     - Thread-safe singleton pattern
     - Separate log files per session

#### Design Patterns Used

- **Factory Pattern**: Logger instantiation via `get_logger()`
- **Singleton Pattern**: Single logger instance per module
- **Strategy Pattern**: Different word cloud generation strategies (frequency vs. TF-IDF)
- **Caching Pattern**: LRU cache decorators for expensive operations

---

### 🏗️ Frontend/Backend Architecture

The application follows a **separation of concerns** architecture with distinct backend and frontend components:

#### Two-Stage Container Architecture

Our Docker deployment uses a **sequential container orchestration** pattern:

##### Stage 1: Backend Processing Container

- **Purpose**: Heavy data preprocessing and transformation
- **Process**: Runs `data_processor.py` to:
  - Load raw CSV datasets from Kaggle
  - Clean and validate data (remove nulls, filter outliers)
  - Transform data into optimized formats
  - Generate `.parquet` files for fast columnar storage
  - Serialize NLP models to `.pkl` files
- **Lifecycle**: Automatically shuts down after successful completion
- **Output**: Persisted files in `data/processed/` volume

##### Stage 2: Frontend Application Container

- **Purpose**: Lightweight web interface for data visualization
- **Process**: Runs Streamlit application
- **Data Access**: Reads preprocessed `.parquet` and `.pkl` files
- **Lifecycle**: Runs continuously to serve the web application
- **Resources**: Minimal CPU/memory footprint

#### Architecture Benefits

✅ **Separation of Concerns**:
- Backend handles computationally expensive ETL operations
- Frontend focuses solely on visualization and user interaction

✅ **Improved Stability**:
- Frontend never performs heavy preprocessing
- No risk of UI crashes during data processing
- Graceful failure isolation

✅ **Resource Efficiency**:
- Backend container only runs when data updates are needed
- Frontend container remains lightweight and responsive
- Optimized resource allocation per workload type

✅ **Faster Startup**:
- Frontend launches instantly with preprocessed data
- No waiting for data processing on application start
- Better user experience

---

### 🔄 Continuous Integration (Pre-Commit)

We maintain code quality through **automated pre-commit checks**:

#### Pre-Commit Hooks

Our `.pre-commit-config.yaml` includes:

1. **Code Quality**
   - ✅ `ruff`: Fast Python linter and formatter
   - ✅ `ruff-format`: Code formatting (PEP 8 compliant)
   - ✅ `mypy`: Static type checking

2. **File Integrity**
   - ✅ `trailing-whitespace`: Remove trailing whitespace
   - ✅ `end-of-file-fixer`: Ensure files end with newline
   - ✅ `check-merge-conflict`: Detect merge conflict markers
   - ✅ `check-toml`: Validate TOML syntax
   - ✅ `check-yaml`: Validate YAML syntax

3. **Testing**
   - ✅ `pytest`: Run unit tests before commit

#### Running Pre-Commit Checks

```bash
# Install pre-commit hooks (one-time setup)
uv run pre-commit install

# Run on all files manually
uv run pre-commit run --all-files

# Run specific hooks
uv run ruff check .
uv run ruff format .
uv run mypy src
uv run pytest
```

#### Complete Pre-Commit Workflow

For detailed pre-commit procedures, see our comprehensive guide:

📖 **[Pre-Commit Workflow Playbook](docs/playbook-precommit.md)**

This playbook covers:
- Code documentation with Pyment
- Linting and formatting commands
- Testing and coverage
- Documentation generation with MkDocs
- Full pre-commit checklist

---

### 📚 Documentation

We use **MkDocs** with the **Material theme** for comprehensive documentation.

#### Documentation Structure

- **API Reference**: Auto-generated from docstrings using `mkdocstrings`
- **Playbooks**: Step-by-step guides for common tasks
  - Environment setup
  - Pre-commit workflow
  - Troubleshooting
  - GCP deployment
- **User Guides**: How to use the application features

#### Serving Documentation Locally

```bash
# Start documentation server
uv run hatch run docs:serve

# Access at http://127.0.0.1:8000
```

#### Building Documentation

```bash
# Build static documentation site
uv run hatch run docs:build

# Deploy to GitHub Pages
uv run hatch run docs:deploy
```

#### Documentation Configuration

- **Tool**: MkDocs with Material theme
- **Plugins**:
  - `mkdocstrings`: API reference generation
  - `gen-files`: Dynamic content generation
  - `section-index`: Automatic section indexing
  - `include-markdown`: Markdown file inclusion
- **Auto-generation**: `scripts/gen_ref_pages.py` generates API docs from source code

📖 **[View Full Documentation](http://127.0.0.1:8000)** (after running `docs:serve`)

---

### 📝 Logger

Our custom logging system provides **structured, colorful logs** for better debugging:

#### Features

- **Color-Coded Output**: Different colors for DEBUG, INFO, WARNING, ERROR, CRITICAL
- **File Rotation**: Automatic log rotation (5MB files, 3 backups)
- **Dual Output**: Console and file handlers
- **Session-Based**: Separate log files per application run
- **Thread-Safe**: Safe for concurrent operations

#### Usage

```python
from mangetamain.utils.logger import get_logger

logger = get_logger()

logger.debug("Debugging information")
logger.info("Processing started")
logger.warning("Deprecated feature used")
logger.error("Failed to load data")
logger.critical("System shutdown required")
```

#### Log Storage

Logs are stored in `logs/app/` with timestamped filenames:
```
logs/app/
├── app_20251028_143052.log
├── app_20251028_143052.log.1
└── app_20251028_143052.log.2
```

---

### 🚀 Continuous Deployment

We use **GitHub Actions** for automated deployment to our Google Cloud VM.

#### CI/CD Pipeline

Our `.github/workflows/deploy.yml` implements a **two-stage pipeline**:

##### Stage 1: Security Scan

- **Tool**: [Safety CLI](https://github.com/pyupio/safety)
- **Purpose**: Scan dependencies for known security vulnerabilities
- **Trigger**: Every push to `main` branch
- **Action**: Fails pipeline if vulnerabilities found

```yaml
security:
  runs-on: ubuntu-latest
  steps:
    - uses: pyupio/safety-action@v1
      with:
        api-key: ${{ secrets.SAFETY_API_KEY }}
```

##### Stage 2: Build & Deploy

Only runs if security scan passes:

1. **Build Docker Image**
   - Multi-stage build for optimized image size
   - Tags: `latest` and `sha-<commit-sha>`
   - Push to GitHub Container Registry (GHCR)

2. **Deploy to VM**
   - SSH into Google Cloud VM
   - Pull latest code and Docker images
   - Run `docker compose up -d`
   - Zero-downtime deployment with health checks

3. **Deploy Documentation**
   - Build documentation with MkDocs
   - Deploy to GitHub Pages automatically
   - Available at: `https://shanoether.github.io/kit_big_data_mangetamain/`

#### Deployment Flow

```
Push to main → Security Scan → Build Docker → Push to GHCR → Deploy to VM → Deploy Docs to GitHub Pages
```

#### Environment Variables & Secrets

Required GitHub secrets:
- `SAFETY_API_KEY`: Safety CLI API key
- `SSH_KEY`: Private SSH key for VM access
- `GHCR_PAT`: GitHub Personal Access Token
- `SSH_HOST`: VM IP address (environment variable)
- `SSH_USER`: VM SSH username (environment variable)

#### Manual Deployment

For manual deployment to Google Cloud, see:

📖 **[GCP Deployment Playbook](docs/playbook-deployment-gcloud.md)**

---

### 🧪 Tests

We maintain **comprehensive test coverage** across all modules.

#### Test Coverage

- **Overall Coverage**: ~97%+ across core modules
- **Backend**: 100% coverage on `DataProcessor` and `RecipeAnalyzer`
- **Utils**: 100% coverage on `logger` and helper functions
- **Frontend**: Core Streamlit functions tested with mocking

#### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run coverage run -m pytest
uv run coverage report -m

# Run specific test file
uv run pytest tests/unit/mangetamain/backend/test_recipe_analyzer.py

# Run specific test class
uv run pytest tests/unit/mangetamain/backend/test_recipe_analyzer.py::TestRecipeAnalyzer

# Run specific test method
uv run pytest tests/unit/mangetamain/backend/test_recipe_analyzer.py::TestRecipeAnalyzer::test_preprocess_text
```

Test folder structur mirrors the structure of `src/mangetamain`

#### Testing Tools

- **pytest**: Test framework
- **pytest-cov**: Coverage reporting
- **unittest.mock**: Mocking framework for isolating tests
- **MagicMock**: Mock objects with type hints

#### Coverage Requirements

- **Minimum**: 90% overall coverage (configured in `pyproject.toml`)
- **Target**: 95%+ for production code
- **Docstring Coverage**: 80% minimum (enforced by `interrogate`)

---

### 🔒 Security

Security is a **top priority** in our deployment and development process.

#### Security Measures Implemented

##### 1. Dependency Scanning

- **Tool**: [Safety CLI](https://pyup.io/safety/)
- **Frequency**: Every commit to `main` branch
- **Action**: Automated scan of all Python dependencies
- **Result**: Pipeline fails if vulnerabilities detected

```yaml
# From .github/workflows/deploy.yml
- name: Run Safety CLI to check for vulnerabilities
  uses: pyupio/safety-action@v1
  with:
    api-key: ${{ secrets.SAFETY_API_KEY }}
```

##### 2. VM Security

**Firewall Configuration**:
- Only port 8501 (Streamlit) exposed to public internet
- All other ports blocked by default

**SSH Key Authentication**:
- Password authentication disabled
- Only ED25519 SSH key authentication allowed
- Separate deployment keys for CI/CD

**VM Hardening**:
```bash
# SSH configuration
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
```

##### 3. Secrets Management

- **GitHub Secrets**: All sensitive credentials stored securely
- **Environment Variables**: No hardcoded secrets in code
- `.env` files in `.gitignore`

##### 4. Docker Security

- **Non-root user**: Container runs as non-privileged user
- **Multi-stage build**: Minimizes attack surface
- **Minimal base image**: Debian slim for smaller footprint
- **No secrets in images**: All secrets mounted at runtime

##### 5. Code Security

- **Type checking**: `mypy` enforces type safety
- **Input validation**: All user inputs validated
- **SQL injection prevention**: Uses Polars DataFrames (no raw SQL)
- **XSS prevention**: Streamlit handles output sanitization

#### Security Audit Results

Latest security scan (generated with Safety CLI):

- TODO

#### Reporting Security Issues

Found a security vulnerability? Please report it responsibly:

1. **DO NOT** open a public GitHub issue
2. Email: gardelautrepourdemain@mangetamain.ai
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

---

### ⚡ Performance

We've optimized the application for **fast data processing and rendering**.

#### Performance Optimizations

##### 1. Data Processing

**Polars instead of Pandas**:
- **10-30x faster** for large datasets
- Lazy evaluation for query optimization
- Parallel processing by default
- Lower memory footprint

##### 2. NLP Processing

**Batch Processing with spaCy**:
- Process texts in batches of 100 for **5-10x speedup**
- Pipeline optimization (`disable=["parser", "ner"]`)
- Only lemmatization and POS tagging enabled

```python
# Batch processing in RecipeAnalyzer
for doc in nlp.pipe(texts, batch_size=100, disable=["parser", "ner"]):
    # Process...
```

##### 3. Caching Strategy

**LRU Cache for Expensive Operations**:
- `@lru_cache` on figure generation methods
- Cached preprocessing results
- Memoized word clouds and plots

```python
@lru_cache(maxsize=128)
def frequency_wordcloud(self, recipe_count: int, ...) -> Figure:
    # Expensive operation cached
```

**Streamlit Cache**:
- `@st.cache_data` for data loading
- `@st.cache_resource` for model loading
- Persistent cache across user sessions

##### 4. Lazy Loading

- Data loaded only when needed
- Progressive rendering of dashboards
- Deferred visualization generation

#### Profiling

We use multiple tools for performance profiling:

```bash
# Install profiling tools
uv sync --group dev

# Profile with py-spy (sampling profiler)
uv run py-spy record -o profile.svg -- python src/mangetamain/backend/data_processor.py

# Profile with snakeviz (visualizer)
uv run python -m cProfile -o output.prof src/mangetamain/backend/data_processor.py
uv run snakeviz output.prof
```

Profiling results available in `docs/profiling.md`.

#### Performance Monitoring

- **Application logs**: Track processing times
- **Streamlit metrics**: Monitor page load times
- **Docker stats**: Monitor container resource usage

```bash
# Monitor container performance
docker stats mangetamain
```

---


## 🧑‍💻 Contributing

We welcome contributions! Please follow our contribution guidelines to maintain code quality and consistency.

### 📋 Using Issue Templates

Before starting work, please create an issue using one of our templates:

#### 🐛 Bug Report

Found a bug? Use our **[Bug Report Template](issue_template/bug_report.md)**:

1. Go to **Issues** → **New Issue**
2. Select **Bug report** template
3. Fill in:
   - **Description**: Clear description of the bug
   - **To Reproduce**: Step-by-step reproduction steps
   - **Expected behavior**: What should happen
   - **Environment**: OS, browser, version
   - **Screenshots**: If applicable

#### ✨ Feature Request

Have an idea? Use our **[Feature Request Template](issue_template/feature_request.md)**:

1. Go to **Issues** → **New Issue**
2. Select **Feature request** template
3. Fill in:
   - **Problem description**: What problem does this solve?
   - **Proposed solution**: How should it work?
   - **Alternatives considered**: Other approaches
   - **Additional context**: Screenshots, mockups, etc.

---

## 🌱 Future Improvements

We're continuously working to improve Mangetamain. Here are planned enhancements:

- 🔍 **Recipe Clustering**: ML-based similarity analysis to discover recipe patterns and group similar recipes
- 📄 **PDF Export**: Export dashboards and analysis reports to PDF for offline viewing
- 📊 **Advanced Visualizations**:
  - Interactive 3D plots for multi-dimensional analysis
  - Network graphs for recipe ingredient relationships
  - Heatmaps for user behavior patterns
- ⚙️ **Enhanced CI/CD Pipeline**:
  - Add automated testing stage
  - Manual approval gate before production deployment
- 🧮 **Advanced Analytics**:
  - Time-series forecasting for recipe trends
  - Sentiment analysis on user reviews
  - Anomaly detection for unusual rating patterns
- 🗄️ **Database Migration**:
  - Move from CSV to PostgreSQL for better scalability
  - Implement data versioning
  - Add data backup and recovery procedures

---

## 📊 Project Metrics

- **Test Coverage**: 97%+
- **Number of Tests**: 80+
- **Dependencies**: 40+
- **Supported Python Version**: 3.12+
- **Docker Image Size**: ~850MB (optimized)

---

## 🙏 Acknowledgments

- **Dataset**: [Food.com Recipes and User Interactions](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions/data) from Kaggle
- **Framework**: [Streamlit](https://streamlit.io/) for the interactive web interface
- **Data Processing**: [Polars](https://www.pola.rs/) for high-performance data operations
- **NLP**: [spaCy](https://spacy.io/) for natural language processing
- **Deployment**: [Google Cloud Platform](https://cloud.google.com/) for hosting

---

## 📚 Additional Resources

- 📘 **[Environment Setup Playbook](docs/playbook-env.md)** - Detailed environment configuration
- 📗 **[Pre-Commit Playbook](docs/playbook-precommit.md)** - Code quality workflow
- 📙 **[Troubleshooting Guide](docs/playbook-troubleshooting.md)** - Common issues and solutions
- 📕 **[GCP Deployment Guide](docs/playbook-deployment-gcloud.md)** - Production deployment

---

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 📞 Contact & Support

- 🐛 **Bug Reports and Feature Request**: [GitHub Issues](https://github.com/shanoether/kit_big_data_mangetamain/issues)

- 📧 **Email**: gardelautrepourdemain@mangetamain.ai
- 🌐 **Live App**: [http://34.1.14.43:8501/](http://34.1.14.43:8501/)
