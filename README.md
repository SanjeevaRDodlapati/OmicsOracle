# OmicsOracle

**AI-Powered Gene Expression Analysis with Automated Full-Text Literature Integration**

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

OmicsOracle automates the analysis of gene expression datasets from GEO (Gene Expression Omnibus) by combining AI-powered interpretation with comprehensive full-text literature retrieval and analysis.

---

## 🌟 Key Features

### Automated GEO Analysis
- **Single-command analysis** of any GEO dataset (GSE ID)
- **Metadata extraction** from GEO SOFT files
- **Sample annotation** and experimental design parsing
- **Citation discovery** from PubMed, Semantic Scholar, OpenAlex

### AI-Powered Insights
- **GPT-5.6 reasoning integration** for intelligent analysis
- **Biological context interpretation** from GEO metadata
- **Methodology summarization** from full-text papers
- **Experimental design validation**

### Comprehensive Literature Access
- **6M+ open access papers** via PubMed Central
- **30M+ articles** via Unpaywall
- **Institutional access** (Georgia Tech, Old Dominion)
- **9 fallback sources** including CORE, bioRxiv, arXiv
- **Automatic PDF download** with validation

### Production-Ready API
- **FastAPI backend** with async support
- **HTML dashboard** for interactive analysis
- **RESTful endpoints** with OpenAPI documentation
- **Rate limiting** and error handling
- **Comprehensive logging**

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Virtual environment (recommended)
- OpenAI API key (for AI analysis)

### Installation

```bash
# Clone repository
git clone https://github.com/sdodlapa/OmicsOracle.git
cd OmicsOracle

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the current dependency manifests and required runtime extras
python -m pip install --upgrade pip
python -m pip install -r archive/docs-nov3-2025/requirements/base.txt
python -m pip install -r archive/docs-nov3-2025/requirements/dev.txt
python -m pip install pypdf 'pydantic[email]'
```

The dependency manifests are currently retained under `archive/docs-nov3-2025/requirements/`; the root-level `requirements/` directory is not present in this revision.

### Configuration

Create a local `.env` file from the tracked template, then replace placeholder values as needed:

```bash
cp .env.example .env
```

`OPENAI_API_KEY` is required for AI analysis. Redis is optional; the application falls back when it is unavailable. Never commit `.env` or real credentials.

### Running the Server

```bash
# Standard local start
venv/bin/python -m omics_oracle_v2.api.main

# Institutional networks that require the repository's SSL bypass mode
./start_omics_oracle.sh
```

The startup script disables SSL verification and should only be used on a trusted network where that workaround is required.

The server will start on `http://localhost:8000`

**Access Points:**
- Dashboard: http://localhost:8000/dashboard
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

---

## 📖 Usage

### Web Dashboard

1. Navigate to http://localhost:8000/dashboard
2. Enter a GEO dataset ID (e.g., `GSE290468`)
3. Click "Analyze"
4. View AI-generated insights and downloaded papers

### API Example

```python
import requests

# Search for GEO datasets and publications
response = requests.post(
  "http://localhost:8000/api/agents/search",
  json={
    "search_terms": ["GSE290468"],
    "max_results": 20,
    "enable_semantic": False,
  },
)

result = response.json()
print(result)
```

### Command Line

```bash
# Quick API validation after starting the server
curl -X POST http://localhost:8000/api/agents/search \
  -H 'Content-Type: application/json' \
  -d '{"search_terms":["GSE290468"],"max_results":20,"enable_semantic":false}'
```

---

## 🏗️ Architecture

```
OmicsOracle/
├── omics_oracle_v2/           # Main application package
│   ├── api/                   # FastAPI application
│   │   ├── routes/           # API endpoints
│   │   └── models/           # Request/Response models
│   ├── services/             # Business logic
│   │   ├── geo_service.py    # GEO data processing
│   │   └── fulltext_service.py # PDF download pipeline
│   ├── lib/                  # Core libraries
│   │   ├── pipelines/        # Data processing pipelines
│   │   │   ├── citation_discovery/
│   │   │   ├── url_collection/
│   │   │   └── pdf_download/
│   │   └── search_engines/   # Citation discovery clients
│   └── config/               # Configuration management
├── config/                   # Deployment configuration
│   ├── development.yml
│   ├── production.yml
│   └── nginx.conf
├── tests/                    # Test suite
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/                     # Documentation
│   ├── current/             # Active documentation
│   └── archive/             # Historical docs
└── data/                     # Application data
    ├── pdfs/                # Downloaded papers
    ├── cache/               # Cached metadata
    └── reports/             # Analysis reports
```

---

## 🔬 Pipeline Overview

### 1. Citation Discovery
- Fetch GEO metadata (title, summary, samples)
- Search PubMed for primary publication
- Discover citing papers via:
  - Semantic Scholar (200M papers)
  - OpenAlex (240M works)
  - PubMed/PMC
  - Europe PMC

### 2. Full-Text Collection
- Extract URLs from discovery clients
- Try multiple sources in priority order:
  1. PubMed Central (6M+ OA papers)
  2. Unpaywall (30M+ articles)
  3. Institutional access
  4. CORE, bioRxiv, arXiv
  5. Crossref

### 3. PDF Download & Validation
- Download PDFs with retry logic
- Validate file integrity (magic bytes)
- Parse landing pages for PDF links
- Store with smart caching

### 4. AI Analysis
- Extract key findings from papers
- Summarize experimental methodology
- Interpret biological context
- Generate comprehensive report

---

## 🛠️ Development

### Running Tests

```bash
# Focused tests during development (the global config enforces 85% coverage)
venv/bin/python -m pytest --no-cov path/to/test_file.py

# Current AI configuration and PMC PDF regression checks
venv/bin/python -m pytest -q --no-cov \
  omics_oracle_v2/tests/unit/test_config.py -k AISettings
venv/bin/python -m pytest -q --no-cov \
  omics_oracle_v2/tests/unit/test_pmc_client.py

# Full configured suite (includes the repository-wide coverage gate)
venv/bin/python -m pytest
```

Some legacy and archived tests are not aligned with the active `omics_oracle_v2` package. Treat focused tests for the changed surface as the primary development check and report unrelated collection or coverage failures separately.

### Code Quality

```bash
# Format code
black omics_oracle_v2/ tests/
isort omics_oracle_v2/ tests/

# Lint
flake8 omics_oracle_v2/ tests/
bandit -r omics_oracle_v2/

# Type checking
mypy omics_oracle_v2/
```

### Pre-commit Hooks

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## 📊 Performance

- **Citation Discovery**: 50-100 papers in ~5 seconds
- **PDF Downloads**: 20-30 papers/minute (with validation)
- **AI Analysis**: 30-60 seconds per dataset
- **Total Pipeline**: 2-3 minutes for typical dataset

**Optimization Features:**
- Concurrent downloads (configurable)
- Smart caching (avoid re-downloads)
- Rate limiting (respect API limits)
- Async processing (non-blocking)

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Development Guidelines:**
- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Run pre-commit hooks

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **GEO (NCBI)** - Gene Expression Omnibus database
- **PubMed Central** - Open access full-text articles
- **Unpaywall** - Open access discovery
- **Semantic Scholar** - Citation graph and metadata
- **OpenAlex** - Open scholarly metadata
- **OpenAI** - GPT-5.6 reasoning models for AI analysis

---

## 📞 Contact

**Author**: Sanjeeva Dodlapati  
**Email**: sdodlapa@gmail.com  
**GitHub**: [@sdodlapa](https://github.com/sdodlapa)

---

## 🗺️ Roadmap

### Current (v2.0)
- ✅ GEO metadata extraction
- ✅ Citation discovery (4 sources)
- ✅ Full-text download (9 sources)
- ✅ AI-powered analysis
- ✅ Web dashboard
- ✅ RESTful API

### Planned (v2.1)
- [ ] Bulk dataset analysis
- [ ] Custom report templates
- [ ] Export to multiple formats
- [ ] Advanced filtering options
- [ ] Collaborative features

### Future (v3.0)
- [ ] Direct GEO data analysis
- [ ] Differential expression
- [ ] Pathway enrichment
- [ ] Integration with other databases
- [ ] Machine learning predictions

---

## 📚 Documentation

- [Installation Guide](docs/current/INSTALLATION.md)
- [API Reference](docs/current/API_REFERENCE.md)
- [Configuration Guide](config/README.md)
- [Architecture Overview](docs/current/ARCHITECTURE.md)
- [AI Analysis Cache Assessment](docs/reports/AI_ANALYSIS_CACHE_ASSESSMENT_2026-07-26.md)

For more documentation, see the [docs/](docs/) directory.

---

**Made with ❤️ by the OmicsOracle Team**
