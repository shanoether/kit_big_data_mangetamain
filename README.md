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

4. **Ratings Dashboard** - Rating distributions and popularity analysis
3. **Trends** - Temporal trends and popular recipe categories
2. **User Analysis** - User behavior patterns and engagement metrics
1. **Recipe Analysis** - Deep dive into recipe characteristics and ingredients


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

### Local Setup

```bash
# Clone repository
git clone https://github.com/shanoether/kit_big_data_mangetamain.git
cd kit_big_data_mangetamain

# Install dependencies
uv sync

# Download spaCy model
uv run python -m spacy download en_core_web_sm
```

### Data Preparation

1. Download [Food.com dataset](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions/data)
2. Place `RAW_interactions.csv` and `RAW_recipes.csv` in `data/raw/`
3. Run preprocessing:

```bash
uv run python src/mangetamain/backend/data_processor.py
```

This generates optimized `.parquet` files and a cached `recipe_analyzer.pkl` in `data/processed/`.

### Launch Application

```bash
uv run streamlit run src/mangetamain/streamlit_ui.py
```

Access at `http://localhost:8501`

### Docker Deployment

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
├── src/mangetamain/
│   ├── streamlit_ui.py              # Main application entry
│   ├── backend/
│   │   ├── data_processor.py        # ETL pipeline
│   │   └── recipe_analyzer.py       # NLP analysis
│   ├── frontend/pages/              # Streamlit pages
│   │   ├── overview.py
│   │   ├── recipes_analysis.py
│   │   ├── users_analysis.py
│   │   ├── trends.py
│   │   └── dashboard.py
│   └── utils/
│       ├── logger.py                # Custom logging
│       └── helper.py                # Data loading utilities
├── tests/unit/                      # Unit tests
├── data/
│   ├── raw/                         # CSV input files
│   └── processed/                   # Parquet & pickle outputs
├── docs/                            # MkDocs documentation
├── .github/workflows/deploy.yml     # CI/CD pipeline
├── docker-compose.yml               # Production deployment
├── Dockerfile                       # Multi-stage build
└── pyproject.toml                   # Dependencies & config
```

---

## 💻 Development Functionalities

### 🎯 Object-Oriented Programming (OOP)

The project follows **OOP best practices** with a clean, modular architecture. However, the object-oriented approach is very basic as `Streamlit` implements its own logic and is not made to be run into different classes.

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

- **Separation of Concerns**
  - Backend handles computationally expensive ETL operations
  - Frontend focuses solely on visualization and user interaction
- **Improved Stability**:
  - Frontend never performs heavy preprocessing
  - No risk of UI crashes during data processing
  - Graceful failure isolation

- **Resource Efficiency**:
  - Backend container only runs when data updates are needed
  - Frontend container remains lightweight and responsive
  - Optimized resource allocation per workload type
- **Faster Startup**:
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
# Pre-commit checks
uv run pre-commit install

# Run on all files manually
uv run pre-commit run --all-files

# Linting & formatting
uv run ruff check .
uv run ruff format .

# Type checking
uv run mypy src
```

For detailed pre-commit procedures, see our comprehensive guide:

📖 **[Pre-Commit Workflow Playbook](docs/playbook-precommit.md)**


---

### 📚 Documentation

We use **MkDocs** with the **Material theme** for comprehensive documentation.

#### Documentation Structure

- [Available on GitHub](https://shanoether.github.io/kit_big_data_mangetamain/): Documentation is automatically updated during deployment and published on GitHub Pages.
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

- **Overall Coverage**: ~90%+ across core modules
- **Backend**: 100% coverage on `DataProcessor` and `RecipeAnalyzer`
- **Utils**: 100% coverage on `logger` and helper functions
- **Frontend**: Core Streamlit functions tested with mocking

#### Running Tests

```bash
# Run all tests
uv run pytest

# With coverage
uv run pytest --cov=src --cov-report=html

# Specific test
uv run pytest tests/unit/mangetamain/backend/test_recipe_analyzer.py
```

---

## 🔒 Security

- **Dependency Scanning**: Automated Safety CLI checks on every commit
- **Firewall**: Only port 443 exposed
- **SSH**: Key-based authentication only, no passwords
- **Docker**: Non-root user, minimal base image
- **Secrets**: GitHub Secrets for credentials, no hardcoded values
- **Errors Page**: Users do not get exposed to precise error messages but generic ones to avoid exploitation.
- **HTTPS Connection**: Secure connection through HTTPS with certificate generated with `letsencrypt`.
---

## ⚡ Performance

We currently have some unresolved performance issues. The loading of different pages is slow despite the various techniques we set up to reduce lagging.

**Optimizations:**
- **Polars**: 10-30x faster than Pandas for large datasets
- **Batch Processing**: spaCy processes 100 texts at a time
- **Caching**: `@st.cache_data` for data, `@st.cache_resource` for models
- **Lazy Loading**: Data loaded only when needed

**Profiling:**
```bash
uv run py-spy record -o profile.svg -- python src/mangetamain/backend/data_processor.py
```

---

## 🧑‍💻 Contributing

Use our issue templates for bug reports or feature requests:

- **Bug Report**: [`issue_template/bug_report.md`](issue_template/bug_report.md)
- **Feature Request**: [`issue_template/feature_request.md`](issue_template/feature_request.md)

---

## 🌱 Future Improvements

We're continuously working to improve *Mangetamain*. Here are planned enhancements:

- 🔍 **Recipe Clustering**: ML-based similarity analysis to discover recipe patterns and group similar recipes
- 📊 **Advanced Visualizations**:
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
  - Move from Parquet to PostgreSQL for better scalability with an API endpoint for the frontend to connect to
  - Implement data versioning
  - Add data backup and recovery procedures

---

## 📊 Project Metrics

- **Test Coverage**: 90%+
- **Python Version**: 3.12+
- **Docker Image**: ~1.5GB (multi-stage optimized)
- **Lines of Code**: ~5,000

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

MIT License - see [LICENSE](LICENSE) file

---

## 📞 Contact

- **Issues**: [GitHub Issues](https://github.com/shanoether/kit_big_data_mangetamain/issues)
- **Email**: gardelautrepourdemain@mangetamain.ai
- **Live App**: [https://mangetamain.duckdns.org/](https://mangetamain.duckdns.org/)
