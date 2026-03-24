# Newsroom Watch

A Django-based platform for scraping news articles and analyzing them with LLMs. It provides a REST API for managing newspapers, scrapers, articles, and AI-powered analysis tools.

## Setup

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

By default, SQLite is used. To use PostgreSQL, set the `DB_URL` environment variable:

```bash
export DB_URL=postgres://user:password@host:5432/dbname
```

## API

The REST API is served at `/` (Django Ninja, auto-docs at `/docs`).

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Summary stats and indicator averages |
| GET | `/newspapers` | List newspapers with article counts and indicators |
| GET | `/newspapers/{nid}` | Newspaper detail with tags |
| GET | `/newspapers/{nid}/articles` | Paginated article list |
| GET | `/newspapers/{nid}/articles/{aid}` | Full article with analyses |
| GET | `/newspapers/{nid}/scrapers` | List scrapers and their history |
| POST | `/newspapers/{nid}/scrapers` | Create a new scraper |
| POST | `/newspapers/{nid}/scrapers/{sid}/code` | Update scraper code |
| POST | `/newspapers/{nid}/scrapers/{sid}/urls` | Add a URL to a scraper |
| GET | `/article?url=...` | Look up article by URL |
| GET | `/tools` | List analysis tools |
| POST | `/run/{action}` | Trigger `parse`, `analyze`, or `prepare` in background |
| GET | `/log/{lid}` | Fetch run log output |

The Django admin (`/admin/`) is the primary interface for configuring newspapers, scrapers, analysis tools, and indicators.

## Scraping

Scrapers are Python code snippets stored in the database (via `NewspaperScraper`). To add a newspaper:

1. Create a `Newspaper` in the admin.
2. Create a `NewspaperScraper` for it, add target URLs, and write the scraper code.
3. Enable the scraper and run:

```bash
python manage.py parse
# or for a specific scraper/URL:
python manage.py parse --id <scraper_id> --url <url>
```

Scraper code runs via `exec()` with helper functions available in the execution context:

- `save_article(NEWSPAPER, article_id, url, title, content, summary, media, author, published)` — persist an article
- `_fetch(url)` — HTTP GET with browser headers
- `_soup(html)` — parse HTML with BeautifulSoup
- `_clean(el)` — strip scripts/nav/footer elements
- `_inner_text(el)` — extract clean text from an element
- `_summarize(text)` — extract a short summary from text
- `_json_ld(soup)` — extract JSON-LD structured data
- `_first_meta(soup, names)` — get a meta tag value by property/name
- `_pick_image(soup)`, `_author_from_meta(soup)`, `_published_from_meta(soup)` — common metadata extractors
- `_id_from_url(url)` — derive an article ID from the URL path
- `NEWSPAPER` — the newspaper ID for the current scraper
- `URL` — the current URL being scraped

## AI Analysis

Analysis tools are configured in the admin as `ArticleAnalysisTool` records. Each tool specifies:
- An OpenAI-compatible model name to use
- A system prompt (passed at inference time)
- Which article fields to analyze (title, content, summary, media)
- Which `Indicator` metrics to extract from the response (expected as JSON)

The analysis commands use the OpenAI client. Configure it with environment variables:

```bash
export OPENAI_API_KEY=your-api-key
export OPENAI_BASE_URL=https://openrouter.ai/api/v1  # default, can be any OpenAI-compatible endpoint
```

**Check API connectivity and list available models:**
```bash
python manage.py prepare
```

**Run analysis** on all unanalyzed articles:
```bash
python manage.py analyze
# or for a specific tool:
python manage.py analyze --id <tool_name>
```

Results are stored as `ArticleAnalysis` (raw LLM JSON output) and `ArticleIndicator` (extracted float values per metric). Indicator averages are surfaced through the API on newspapers, tags, and the index endpoint.

## Production

The project uses `granian` as an ASGI server and `whitenoise` for static file serving:

```bash
python manage.py collectstatic
granian newsroom.asgi:application
```

## Newsroom Dashboard
Newsroom Dashboard is the interface for the whole newsroom analysis tool, and offers a few visualization options based on the elements collected by the analysis tools.
<img width="1280" height="734" alt="image" src="https://github.com/user-attachments/assets/e027fdef-ef5c-47b3-99c2-2c1519a62d63" />

It also offers the possibility to edit the code for the scraping directly from the interface
<img width="1280" height="838" alt="image" src="https://github.com/user-attachments/assets/91a68174-e715-4336-a249-792ef49c175e" />


