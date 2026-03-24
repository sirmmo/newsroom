# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run development server
python manage.py runserver

# Apply migrations
python manage.py migrate

# Create new migrations
python manage.py makemigrations

# Run tests
python manage.py test

# Run tests for a single app
python manage.py test newspaper

# Scrape articles from configured newspapers
python manage.py parse
python manage.py parse --id <scraper_id> --url <url>

# Run AI analysis on articles
python manage.py analyze
python manage.py analyze --id <tool_name>

# Pull/create Ollama models from DB-configured tools
python manage.py prepare
```

Production uses `granian` as the ASGI server. Database defaults to SQLite; set `DB_URL` env var for PostgreSQL.

## Architecture

Django 5.2 project with three apps:

- **`newspaper`** — core app. Contains all models, the REST API, and management commands.
- **`events`** — `Event` and `EventGroup` models for tracking real-world events.
- **`coverage`** — `EventCoverage` links `Event` to `Article`, representing which articles cover which events.

### API

All REST endpoints are defined in `newspaper/views.py` using a single `NinjaExtraAPI` instance (`api`). It is mounted at the root in `newsroom/urls.py`. Schemas are defined inline in the same file using `ModelSchema` from `django-ninja`.

The API exposes endpoints for newspapers, articles, scrapers, analysis tools, run logs, and triggering management commands asynchronously via `POST /run/{action}` (runs `parse`, `analyze`, or `prepare` in a background thread, returning a `RunDump` log ID).

### Scraper system

Scrapers are Python code stored as text in `NewspaperScraper.scraper` (a TextField). The `parse` management command fetches this code from the DB and executes it via `exec()` with a context dictionary of helper functions (`_fetch`, `_soup`, `_clean`, `_inner_text`, `_summarize`, `_json_ld`, etc.) and `save_article`. This means scraper logic is configured at runtime through the admin or API, not in source files.

`NewspaperScraper` has full history tracking via `django-simple-history`.

### AI analysis pipeline

`ArticleAnalysisTool` records define a system prompt, an Ollama model name, an `internal_name` (the model variant created with the system prompt baked in), and flags for which article fields to analyze (`applies_to_title`, `applies_to_content`, `applies_to_summary`, `applies_to_media`).

The `analyze` command connects to a remote Ollama instance, creates named model variants from `ArticleAnalysisTool` records, then runs each unanalyzed article through the relevant tools. Results are stored as `ArticleAnalysis` with parsed JSON in `result`, and per-indicator float values are stored as `ArticleIndicator` records linked to both the article and the analysis.

The `analyze` command also supports OpenRouter (via the `openai` SDK) as an alternative backend (client is instantiated but routing between Ollama and OpenRouter is not fully wired).

### Key models (all in `newspaper/models.py`)

| Model | Purpose |
|---|---|
| `Newspaper` | A news source with a base URL and tags |
| `NewspaperScraper` | Executable Python scraper code + URLs to scrape |
| `NewspaperFeed` | RSS/Atom feed URL for a newspaper |
| `Article` | Scraped article with title, content, summary, media, author |
| `ArticleAnalysisTool` | LLM tool definition (system prompt + model + field flags) |
| `ArticleAnalysis` | Raw LLM output for one article+tool combination |
| `Indicator` | Named float metric with min/max/label metadata |
| `ArticleIndicator` | Extracted indicator value for a specific article |
| `RunDump` | Execution log for management command runs |
| `Event` / `EventGroup` | Real-world events (in `events` app) |
| `EventCoverage` | Article-to-Event linkage (in `coverage` app) |
