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

## Environment variables

| Variable | Purpose |
|---|---|
| `DB_URL` | PostgreSQL connection string (overrides default SQLite) |
| `OPENAI_BASE_URL` | LLM API base URL (defaults to `https://openrouter.ai/api/v1`) |
| `OPENAI_API_KEY` | API key for the LLM backend |

## Architecture

Django 5.2 project with three apps:

- **`newspaper`** — core app. Contains all models, the REST API, and management commands.
- **`events`** — `Event` and `EventGroup` models for tracking real-world events.
- **`coverage`** — `EventCoverage` links `Event` to `Article`, representing which articles cover which events.

The `events` and `coverage` apps have models and admin but no active API endpoints; all REST API surface lives in `newspaper/views.py`.

### API

All REST endpoints are defined in `newspaper/views.py` using a single `NinjaAPI` instance (`api`). It is mounted at the root in `newsroom/urls.py`. Schemas are defined inline in the same file using `ModelSchema` from `django-ninja`.

Key endpoints:
- `GET /` — aggregate stats and per-tag indicator averages
- `GET /newspapers` — paginated list (`?mode=parsed|all`)
- `GET /newspapers/{nid}/articles/{aid}` — full article with analyses
- `GET /article?url=<url>` — fetch a single article by URL
- `POST /run/{action}` — runs `parse`, `analyze`, or `prepare` in a background thread, returns a `RunDump` log ID
- `GET /log/{lid}` — poll RunDump output

### Scraper system

Scrapers are Python code stored as text in `NewspaperScraper.scraper` (a TextField). The `parse` management command fetches this code from the DB and executes it via `exec()` with a context dictionary of helper functions and `save_article`. This means scraper logic is configured at runtime through the admin or API, not in source files.

Context available to scraper code: `NEWSPAPER`, `URL`, `HEADERS`, `save_article`, `_save`, `_fetch`, `_soup`, `_clean`, `_inner_text`, `_summarize`, `_parse_iso`, `_json_ld`, `_first_meta`, `_pick_image`, `_author_from_meta`, `_published_from_meta`, `_id_from_url`.

`NewspaperScraper` has full history tracking via `django-simple-history`.

### AI analysis pipeline

`ArticleAnalysisTool` records define a system prompt, a model name, an `internal_name`, and flags for which article fields to analyze (`applies_to_title`, `applies_to_content`, `applies_to_summary`, `applies_to_media`).

The `analyze` command uses the OpenAI SDK pointed at OpenRouter by default (`OPENAI_BASE_URL` / `OPENAI_API_KEY`). It runs each unanalyzed article through the relevant active tools. Results are stored as `ArticleAnalysis` with parsed JSON in `result`, and per-indicator float values are stored as `ArticleIndicator` records linked to both the article and the analysis.

### Key models (all in `newspaper/models.py`)

`Newspaper.id` and `Article.id` are UUID strings, not auto-increment integers.

| Model | Purpose |
|---|---|
| `Tag` | Category/name label attached to newspapers |
| `Newspaper` | A news source with a base URL and tags (UUID PK) |
| `NewspaperSubpage` | A URL associated with a scraper |
| `NewspaperScraper` | Executable Python scraper code + M2M to `NewspaperSubpage` URLs |
| `NewspaperFeed` | RSS/Atom feed URL for a newspaper |
| `Article` | Scraped article with title, content, summary, media, author (UUID PK) |
| `ArticleAnalysisTool` | LLM tool definition (system prompt + model + field flags) |
| `ArticleAnalysis` | Raw LLM output for one article+tool combination |
| `Indicator` | Named float metric with min/max/label metadata |
| `ArticleIndicator` | Extracted indicator value for a specific article |
| `RunDump` | Execution log for management command runs |
| `Event` / `EventGroup` | Real-world events (in `events` app) |
| `EventCoverage` | Article-to-Event linkage (in `coverage` app) |
