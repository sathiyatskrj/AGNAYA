# Contributing to AGNAYA

Thank you for your interest in contributing to **AGNAYA** (Adaptive Geospatial Network for Heatwave Analytics and Yield Assessment). We welcome contributions from power systems engineers, climate researchers, urban disaster planners, software developers, and municipal officials.

---

## Code of Conduct

We are committed to providing a welcoming, inclusive, and professional environment. Please treat all contributors and community members with respect and courtesy.

---

## How Can You Contribute?

1. **Reporting Bugs**: Check existing issues before opening a new bug report. Provide detailed reproduction steps, system environment, and relevant stack traces.
2. **Improving Physical Models**: Contributions that refine transformer thermal models (IEEE C57.91), line ampacity equations (IEEE Std 738), or biometeorological indices (UTCI / WBGT) with grounded empirical data are highly encouraged.
3. **Extending Grounded Datasets**: Adding localized municipal ward topologies, hospital bed capacities, or distribution feeder maps for other vulnerable Indian cities.
4. **Enhancing Performance & UI**: Optimizing DC power flow matrix solvers, expanding Streamlit UI components, or improving accessibility.

---

## Development Workflow

### 1. Fork & Clone
```bash
git clone https://github.com/sathiyatskrj/AGNAYA.git
cd AGNAYA
```

### 2. Environment Setup
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Running Verification Suite
Before making a pull request, ensure all 12 multi-model test suites pass cleanly:
```bash
python test_system.py
```

### 4. Running the Applications
```bash
# Streamlit Dashboard
streamlit run app.py --server.port 8501

# FastAPI REST Microservice
uvicorn api:app --host 127.0.0.1 --port 8000 --reload
```

---

## Pull Request Guidelines

- Branch naming: `feature/your-feature-name` or `fix/issue-description`.
- Ensure `python test_system.py` executes with all tests passing.
- Document any new mathematical equations or statutory parameters in `MODEL_AND_METHODOLOGY.md`.
- Keep pull requests focused on a single logical change.
