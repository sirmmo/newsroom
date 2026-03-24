from django.core.management.base import BaseCommand, CommandError
import requests
from bs4 import BeautifulSoup as bs
from newspaper.models import * 
import datetime
import time
import traceback

import re, json, datetime as _dt
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup as _bs


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

HEADERS_LOCAL = HEADERS

def save_article(NEWSPAPER, article_id, url, title, content, summary, media, author, published):
    a, c = Article.objects.get_or_create(newspaper_id=NEWSPAPER, in_paper_id=article_id)
    a.url = url
    a.title = title
    a.content = content
    a.summary = summary
    a.media = media
    a.author = author
    a.published = published
    a.save()


to_store= ""

def xprint(*args):
    global to_store
    to_store += " ".join(map(str,args))+ "\n"
    print(args)


def _fetch(url, allow_redirects=True):
    resp = requests.get(url, headers=HEADERS_LOCAL, timeout=20, allow_redirects=allow_redirects)
    resp.raise_for_status()
    return resp

def _soup(html):
    return _bs(html, "html.parser")

def _clean(el):
    # Remove non-content nodes commonly present
    for tag in el.find_all(["script","style","noscript","aside","svg","figure","figcaption","iframe","button","form","header","footer","nav"]):
        tag.decompose()
    return el

def _inner_text(el):
    txt = el.get_text("\n", strip=True)
    # collapse multiple newlines
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    return txt.strip()

def _summarize(text, max_chars=500):
    # primitive summary: first 3 paragraphs up to max_chars
    parts = [p.strip() for p in text.split("\n") if p.strip()]
    out = []
    total = 0
    for p in parts[:6]:
        if total + len(p) > max_chars and out:
            break
        out.append(p)
        total += len(p)
    return " ".join(out)[:max_chars].strip()

def _parse_iso(ts):
    if not ts: return None
    try:
        # Try strict ISO or RFC3339
        return _dt.datetime.fromisoformat(ts.replace("Z","+00:00"))
    except Exception:
        pass
    # Try common formats
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%a, %d %b %Y %H:%M:%S %Z"):
        try:
            return _dt.datetime.strptime(ts, fmt)
        except Exception:
            continue
    return None

def _json_ld(soup):
    data = []
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            blob = json.loads(tag.string or tag.text or "{}")
            if isinstance(blob, list):
                data.extend(blob)
            else:
                data.append(blob)
        except Exception:
            continue
    return data

def _first_meta(soup, names):
    for n in names:
        el = soup.find("meta", attrs={"property": n}) or soup.find("meta", attrs={"name": n})
        if el and el.get("content"): return el["content"].strip()
    return None

def _pick_image(soup):
    # prefer og:image / twitter:image
    return _first_meta(soup, ["og:image", "twitter:image", "image"])

def _author_from_meta(soup):
    return _first_meta(soup, ["author", "article:author", "og:article:author", "parsely-author"])

def _published_from_meta(soup):
    return _first_meta(soup, ["article:published_time", "og:article:published_time", "parsely-pub-date", "publish_date", "date", "dc.date", "rnews:datePublished"])

def _id_from_url(url):
    # slug or numeric id from the path
    path = urlparse(url).path.rstrip("/")
    if not path or path == "/":
        return url
    slug = path.split("/")[-1]
    # fallback to full path if too short
    return slug if len(slug) >= 3 else path

def _save(final):
    save_article(
        NEWSPAPER,
        final["article_id"],
        final["url"],
        final["title"],
        final["content"],
        final["summary"],
        final["media"],
        final["author"],
        final["published"],
    )



class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--id", nargs="?", type=int)
        parser.add_argument("--rd", nargs="?", type=str)
        parser.add_argument("--url", nargs="?", type=str)

    def handle(self, *args, **options):

        if options['rd']:
            rd = RunDump.objects.get(id=options['rd'])
        else:
            rd = RunDump()
        rd.start = datetime.datetime.now()
        rd.action = "parse"
        rd.save()
        to_parse = NewspaperScraper.objects.filter(enabled=True)
        if options['id']:
            to_parse = to_parse.filter(id__in=[options['id']])
        for ns in to_parse:
            xprint(">", ns.newspaper)
            if options['url']:
                urls = [options['url']]
            else:
                urls = ns.urls.all().values_list('url', flat=True)
            for u in urls:
                xprint(">>",u)
                try:
                    ctx = {
                        "NEWSPAPER": ns.newspaper.id,
                        "URL": u,
                        "HEADERS": HEADERS,
                        "HEADERS_LOCAL": HEADERS,
                        "save_article": save_article,
                        "print":xprint,
                        "_save": _save,
                        "_fetch":_fetch,
                        "_soup": _soup,
                        "_clean": _clean,
                        "_inner_text": _inner_text,
                        "_summarize": _summarize,
                        "_parse_iso": _parse_iso,
                        "_json_ld": _json_ld,
                        "_first_meta": _first_meta,
                        "_pick_image": _pick_image,
                        "_author_from_meta": _author_from_meta,
                        "_published_from_meta": _published_from_meta,
                        "_id_from_url": _id_from_url,

                    }
                    exec(ns.scraper, globals(), ctx)
                except Exception as ex:
                    xprint("EX", ex)
                    xprint(traceback.format_exc())
                rd.run = to_store
                #rd.end = datetime.datetime.now()
                rd.save()

        for nf in NewspaperFeed.objects.filter(fmt="rss"):
            xprint(">", nf.newspaper, nf.url)

        rd.run = to_store
        rd.end = datetime.datetime.now()
        rd.save()