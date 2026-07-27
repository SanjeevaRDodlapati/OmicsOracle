# OmicsOracle Coding Instructions

## Active Application

- Treat `omics_oracle_v2/` as the active application package.
- The FastAPI entry point is `omics_oracle_v2.api.main:app`.
- The dashboard is a single static HTML/JavaScript file at `omics_oracle_v2/api/static/dashboard_v2.html`; it does not use React or another frontend state framework.
- Treat `archive/`, `extras/`, and historical documentation as reference material unless the task explicitly targets them. Do not restore obsolete imports from those directories.

## Local Setup

Use Python 3.11 and the repository virtual environment:

```bash
python3.11 -m venv venv
venv/bin/python -m pip install --upgrade pip
venv/bin/python -m pip install -r archive/docs-nov3-2025/requirements/base.txt
venv/bin/python -m pip install -r archive/docs-nov3-2025/requirements/dev.txt
venv/bin/python -m pip install pypdf 'pydantic[email]'
cp .env.example .env
```

Never commit `.env`, API keys, tokens, passwords, or cached model/paper content. The tracked `.env.example` must contain placeholders only.

Start the application with:

```bash
venv/bin/python -m omics_oracle_v2.api.main
```

Expected local endpoints:

- Dashboard: `http://localhost:8000/dashboard`
- API docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health/`

`start_omics_oracle.sh` intentionally disables SSL verification for institutional networks. Use it only when that trusted-network workaround is required. The current Makefile contains legacy package and dependency paths and is not authoritative for setup or startup.

## Validation

`pytest.ini` applies an 85% repository-wide coverage threshold. Use focused tests with `--no-cov` while developing, then report any unrelated global-suite failures separately.

```bash
venv/bin/python -m pytest -q --no-cov path/to/test_file.py
venv/bin/python -m compileall -q omics_oracle_v2 scripts tests
git diff --check
```

Current focused checks for AI configuration and PMC fallback behavior are:

```bash
venv/bin/python -m pytest -q --no-cov \
  omics_oracle_v2/tests/unit/test_config.py -k AISettings
venv/bin/python -m pytest -q --no-cov \
  omics_oracle_v2/tests/unit/test_pmc_client.py
```

Known unrelated debt includes stale `GEOSettings.api_key` expectations in `omics_oracle_v2/tests/unit/test_config.py`, legacy test imports for removed modules, and the global coverage gate failing for narrow test selections. Do not fix unrelated failures as part of a focused task.

## Full-Text Policy

- Use legal open-access and institutional providers only: PMC/Europe PMC, Unpaywall, CORE, OpenAlex, Crossref, bioRxiv, arXiv, and configured institutional access.
- Do not add Sci-Hub, LibGen, mirrors, proxy domains, or fallback logic for those services.
- A successful HTTP response is not sufficient PDF validation. Require a PDF content type where available and preserve magic-byte validation in the download path.

## AI Analysis

- The default model is `gpt-5.6-terra` with `high` reasoning effort.
- Supported configured tiers are Luna for fast work, Terra for balanced work, and Sol for deep analysis.
- GPT-5 and reasoning models use the OpenAI Responses API in `omics_oracle_v2/api/helpers/llm.py`; legacy models use Chat Completions.
- Keep model, reasoning effort, temperature, prompt, and system instructions represented in AI cache identity.
- Preserve API keys in settings/environment variables and never log them.

## Cache Boundaries

- Search results use Redis and normally expire after 24 hours.
- AI raw model responses use Redis and expire after seven days.
- Parsed full text uses a seven-day Redis hot tier and a 90-day compressed-disk warm tier.
- Browser analysis panel state is currently not persistent. See `docs/reports/AI_ANALYSIS_CACHE_ASSESSMENT_2026-07-26.md` before changing analysis-panel behavior.
- Server-side cache hits do not restore frontend expand/collapse state; treat those as separate concerns.

## Change Discipline

- Preserve the existing architecture and make focused changes in the owning service or helper.
- Add narrow regression tests for behavior changes.
- Do not modify or delete user changes in a dirty worktree.
- Update active documentation when setup, configuration, API contracts, or operational behavior changes.
