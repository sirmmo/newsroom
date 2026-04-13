# Newsroom Watch

![Python](https://img.shields.io/badge/python-3.8+-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/django-5.2-092E20?logo=django&logoColor=white)
![Django Ninja](https://img.shields.io/badge/API-django--ninja-009688)
![License](https://img.shields.io/badge/license-Apache%202.0-blue)

A Django platform for scraping news articles and running LLM-based analysis on them. Scrapers are Python snippets stored in the database and executed at runtime — no deploys needed to add or update a news source. Analysis tools are similarly configured through the admin, with results exposed as per-article indicator scores through a REST API.

## Quick start

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

SQLite is used by default. For PostgreSQL:

```bash
export DB_URL=postgres://user:password@host:5432/dbname
```

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `DB_URL` | SQLite | PostgreSQL connection string |
| `OPENAI_API_KEY` | — | API key for the LLM backend |
| `OPENAI_BASE_URL` | `https://openrouter.ai/api/v1` | Any OpenAI-compatible endpoint |

## API

Auto-generated docs at `/docs`. The Django admin at `/admin/` is the primary interface for configuring newspapers, scrapers, tools, and indicators.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Summary stats and indicator averages by tag |
| GET | `/newspapers` | List newspapers with article counts and indicators |
| GET | `/newspapers/{nid}` | Newspaper detail with tags |
| GET | `/newspapers/{nid}/articles` | Paginated article list |
| GET | `/newspapers/{nid}/articles/{aid}` | Full article with analyses |
| GET | `/newspapers/{nid}/scrapers` | List scrapers and version history |
| POST | `/newspapers/{nid}/scrapers` | Create a new scraper |
| POST | `/newspapers/{nid}/scrapers/{sid}/code` | Update scraper code |
| POST | `/newspapers/{nid}/scrapers/{sid}/urls` | Add a URL to a scraper |
| GET | `/article?url=...` | Look up article by URL |
| GET | `/tools` | List analysis tools |
| POST | `/run/{action}` | Trigger `parse`, `analyze`, or `prepare` async |
| GET | `/log/{lid}` | Poll run log output |

## Scraping

Scrapers are Python snippets stored in `NewspaperScraper` records. To add a news source:

1. Create a `Newspaper` in the admin.
2. Create a `NewspaperScraper`, add target URLs, and write the scraper code.
3. Enable the scraper, then run:

```bash
python manage.py parse

# Target a specific scraper or URL
python manage.py parse --id <scraper_id> --url <url>
```

Scraper code runs via `exec()` with the following context available:

| Name | Description |
|---|---|
| `NEWSPAPER` | The current newspaper's ID |
| `URL` | The URL being scraped |
| `save_article(...)` | Persist a scraped article |
| `_fetch(url)` | HTTP GET with browser headers |
| `_soup(html)` | Parse HTML with BeautifulSoup |
| `_clean(el)` | Strip scripts, nav, and footer elements |
| `_inner_text(el)` | Extract clean text from an element |
| `_summarize(text)` | Extract a short lead summary |
| `_json_ld(soup)` | Extract JSON-LD structured data |
| `_first_meta(soup, names)` | Get a meta tag value by property/name |
| `_pick_image(soup)` | Extract `og:image` / `twitter:image` |
| `_author_from_meta(soup)` | Extract author from meta tags |
| `_published_from_meta(soup)` | Extract publish date from meta tags |
| `_id_from_url(url)` | Derive an article ID from the URL slug |

Scraper history is tracked automatically via `django-simple-history`.

## AI Analysis

Configure `ArticleAnalysisTool` records in the admin. Each tool specifies:

- An OpenAI-compatible model name
- A system prompt
- Which article fields to analyze (title, content, summary, or media)
- Which `Indicator` metrics to extract from the JSON response

```bash
# Run analysis on all unanalyzed articles
python manage.py analyze

# Run a specific tool
python manage.py analyze --id <tool_name>
```

Results are stored as `ArticleAnalysis` (raw LLM JSON) and `ArticleIndicator` (extracted float values). Indicator averages are aggregated and surfaced through the API on newspapers, tags, and the index endpoint.

## Production

Uses `granian` as the ASGI server and `whitenoise` for static files:

```bash
python manage.py collectstatic
granian newsroom.asgi:application
```
