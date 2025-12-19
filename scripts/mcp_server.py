"""
Thordata MCP Server

This script exposes Thordata-powered tools via the Model Context Protocol (MCP).

Tools:
- search_web(query, engine="google", num=5, location=None, search_type=None):
    Real-time web search using Thordata SERP API
    (Google/Bing/Yandex/DuckDuckGo).

- search_news(query, engine="google", num=5, location=None):
    Convenience wrapper around search_web() with search_type="news".

- read_website(url, js_render=True, country=None, max_chars=15000):
    Scrape and clean any web page using the Universal Scraping API.

- extract_links(url, js_render=False, country=None, max_links=200, unique=True):
    Extract all hyperlinks from a page, returning structured JSON.

Intended to be used from an MCP-compatible client (e.g. Claude Desktop),
but the tool functions can also be imported and called directly from Python.
"""

from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from thordata import (
    ThordataClient,
    Engine,
    ThordataRateLimitError,
    ThordataAuthError,
    ThordataAPIError,
    ThordataConfigError,
)

# ---------------------------------------------------------------------------
# Configuration & client initialization
# ---------------------------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[1]

ENV_PATH = ROOT_DIR / ".env"
load_dotenv(ENV_PATH)

logger = logging.getLogger("thordata.mcp")


@lru_cache
def get_thordata_client() -> ThordataClient:
    scraper_token = os.getenv("THORDATA_SCRAPER_TOKEN")
    public_token = os.getenv("THORDATA_PUBLIC_TOKEN")
    public_key = os.getenv("THORDATA_PUBLIC_KEY")

    if not scraper_token:
        raise ThordataConfigError(
            "THORDATA_SCRAPER_TOKEN is missing. "
            "Please create a .env file at the project root and set your tokens."
        )

    return ThordataClient(
        scraper_token=scraper_token,
        public_token=public_token,
        public_key=public_key,
    )


# Name visible to the MCP client (e.g. Claude)
mcp = FastMCP("Thordata Tools")

_ENGINE_MAP: Dict[str, Engine] = {
    "google": Engine.GOOGLE,
    "bing": Engine.BING,
    "yandex": Engine.YANDEX,
    "duckduckgo": Engine.DUCKDUCKGO,
}

# ---------------------------------------------------------------------------
# Helper: HTML -> cleaned text
# ---------------------------------------------------------------------------


def clean_html_to_text(html: str) -> str:
    """
    Convert raw html into a cleaned plain-text representation.

    - Removes scripts, styles, navigation, footers, SVGs, iframes.
    - Collapses whitespace and drops empty lines.
    """
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "svg", "iframe", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tool 1: Web Search (SERP)
# ---------------------------------------------------------------------------


@mcp.tool()
def search_web(
    query: str,
    engine: str = "google",
    num: int = 5,
    location: Optional[str] = None,
    search_type: Optional[str] = None,
) -> str:
    """
    Use this tool to search the web for real-time information, news, or facts.

    Args:
        query: The search keywords.
        engine: Search engine to use: 'google', 'bing', 'yandex', 'duckduckgo'.
        num: Number of results to retrieve (default: 5).
        location: Optional location string (e.g. 'United States', 'London').
        search_type: Optional search type (e.g. 'shopping', 'news', 'images', 'videos').

    Returns:
        JSON string:
        {
          "engine": "...",
          "query": "...",
          "results": [
            { "rank": 1, "title": "...", "link": "...", "snippet": "..." },
            ...
          ]
        }
    """
    engine_key = (engine or "google").lower()
    engine_enum = _ENGINE_MAP.get(engine_key, Engine.GOOGLE)

    logger.info(
        "[MCP] search_web -> query=%r, engine=%s, num=%s, location=%r, type=%r",
        query,
        engine_key,
        num,
        location,
        search_type,
    )

    extra_params: Dict[str, str] = {}
    if location:
        extra_params["location"] = location
    if search_type:
        extra_params["type"] = search_type

    try:
        client = get_thordata_client()

        results = client.serp_search(
            query=query,
            engine=engine_enum,
            num=num,
            **extra_params,
        )
    except ThordataRateLimitError as e:
        return json.dumps(
            {
                "engine": engine_key,
                "query": query,
                "error_type": "thordata_rate_limit",
                "error": str(e),
            },
            ensure_ascii=False,
            indent=2,
        )
    except ThordataAuthError as e:
        return json.dumps(
            {
                "engine": engine_key,
                "query": query,
                "error_type": "thordata_auth",
                "error": str(e),
            },
            ensure_ascii=False,
            indent=2,
        )
    except ThordataAPIError as e:
        return json.dumps(
            {
                "engine": engine_key,
                "query": query,
                "error_type": "thordata_api",
                "error": str(e),
            },
            ensure_ascii=False,
            indent=2,
        )
    except ThordataConfigError as e:
        return json.dumps(
            {
                "engine": engine_key,
                "query": query,
                "error_type": "thordata_config",
                "error": str(e),
            },
            ensure_ascii=False,
            indent=2,
        )
    except Exception as exc:
        logger.exception("search_web failed: %s", exc)
        return json.dumps(
            {
                "engine": engine_key,
                "query": query,
                "error_type": "unknown",
                "error": str(exc),
            },
            ensure_ascii=False,
            indent=2,
        )

    organic: List[Dict] = results.get("organic") or []
    if not organic:
        return json.dumps(
            {
                "message": "No organic results found.",
                "engine": engine_key,
                "query": query,
            },
            ensure_ascii=False,
            indent=2,
        )

    clean_results: List[Dict[str, str]] = []
    for idx, item in enumerate(organic, start=1):
        clean_results.append(
            {
                "rank": idx,
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet"),
            }
        )

    return json.dumps(
        {
            "engine": engine_key,
            "query": query,
            "results": clean_results,
        },
        ensure_ascii=False,
        indent=2,
    )


# ---------------------------------------------------------------------------
# Tool 1.1: News search (wrapper around search_web)
# ---------------------------------------------------------------------------


@mcp.tool()
def search_news(
    query: str,
    engine: str = "google",
    num: int = 5,
    location: Optional[str] = None,
) -> str:
    """
    Convenience wrapper around search_web() to search for **news**."""
    return search_web(
        query=query,
        engine=engine,
        num=num,
        location=location,
        search_type="news",
    )


# ---------------------------------------------------------------------------
# Tool 2: Read & Clean Web Page (Universal Scraping)
# ---------------------------------------------------------------------------


@mcp.tool()
def read_website(
    url: str,
    js_render: bool = True,
    country: Optional[str] = None,
    max_chars: int = 15000,
) -> str:
    """
    Use this tool to read the content of a specific URL.

    Useful for:
    - Summarizing articles or documentation.
    - Extracting relevant text from dynamic sites.
    """
    logger.info(
        "[MCP] read_website -> url=%r, js_render=%s, country=%r, max_chars=%d",
        url,
        js_render,
        country,
        max_chars,
    )

    try:
        client = get_thordata_client()

        html = client.universal_scrape(
            url=url,
            js_render=js_render,
            output_format="html",
            country=country,
        )
    except ThordataRateLimitError as e:
        return f"Thordata Universal API rate/quota issue: {e}"
    except ThordataAuthError as e:
        return f"Thordata Universal API authentication error: {e}"
    except ThordataAPIError as e:
        return f"Thordata Universal API returned an error: {e}"
    except ThordataConfigError as e:
        return f"Thordata configuration error: {e}"
    except Exception as exc:
        logger.exception("read_website failed: %s", exc)
        return f"Scrape Error: {exc!s}"

    if not html or len(html) < 100:
        return f"Error: Failed to retrieve content or content is empty. URL: {url}"

    clean_text = clean_html_to_text(html)

    if max_chars and len(clean_text) > max_chars:
        clean_text = clean_text[:max_chars]

    return f"Source: {url}\n\n{clean_text}"


# ---------------------------------------------------------------------------
# Tool 3: Extract all links from a page
# ---------------------------------------------------------------------------


@mcp.tool()
def extract_links(
    url: str,
    js_render: bool = False,
    country: Optional[str] = None,
    max_links: int = 200,
    unique: bool = True,
) -> str:
    """
    Extract hyperlinks from the given URL."""
    logger.info(
        "[MCP] extract_links -> url=%r, js_render=%s, country=%r, max_links=%d, unique=%s",
        url,
        js_render,
        country,
        max_links,
        unique,
    )

    try:
        client = get_thordata_client()

        html = client.universal_scrape(
            url=url,
            js_render=js_render,
            output_format="html",
            country=country,
        )
    except ThordataRateLimitError as e:
        return json.dumps(
            {"source": url, "error_type": "thordata_rate_limit", "error": str(e)},
            ensure_ascii=False,
            indent=2,
        )
    except ThordataAuthError as e:
        return json.dumps(
            {"source": url, "error_type": "thordata_auth", "error": str(e)},
            ensure_ascii=False,
            indent=2,
        )
    except ThordataAPIError as e:
        return json.dumps(
            {"source": url, "error_type": "thordata_api", "error": str(e)},
            ensure_ascii=False,
            indent=2,
        )
    except ThordataConfigError as e:
        return json.dumps(
            {"source": url, "error_type": "thordata_config", "error": str(e)},
            ensure_ascii=False,
            indent=2,
        )
    except Exception as exc:
        logger.exception("extract_links failed: %s", exc)
        return json.dumps(
            {"source": url, "error_type": "unknown", "error": str(exc)},
            ensure_ascii=False,
            indent=2,
        )

    if not html or len(html) < 100:
        return json.dumps(
            {
                "source": url,
                "count": 0,
                "links": [],
                "message": "Failed to retrieve content or content is empty.",
            },
            ensure_ascii=False,
            indent=2,
        )

    soup = BeautifulSoup(html, "html.parser")

    links: List[Dict[str, str]] = []
    seen: set[str] = set()

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        text = a.get_text(strip=True) or href
        abs_url = urljoin(url, href)

        if unique:
            if abs_url in seen:
                continue
            seen.add(abs_url)

        links.append(
            {
                "text": text,
                "href": abs_url,
            }
        )

        if max_links and len(links) >= max_links:
            break

    return json.dumps(
        {
            "source": url,
            "count": len(links),
            "links": links,
        },
        ensure_ascii=False,
        indent=2,
    )


# ---------------------------------------------------------------------------
# Run MCP server
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
    )
    print("Thordata MCP Server is running...")
    mcp.run()
