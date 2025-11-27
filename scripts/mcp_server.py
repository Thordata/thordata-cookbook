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
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from thordata import ThordataClient, Engine


# ---------------------------------------------------------------------------
# Configuration & client initialization
# ---------------------------------------------------------------------------

# Resolve project root (two levels above this file: scripts/ -> repo root)
ROOT_DIR = Path(__file__).resolve().parents[1]

# Load .env from the repo root
ENV_PATH = ROOT_DIR / ".env"
load_dotenv(ENV_PATH)

logger = logging.getLogger("thordata.mcp")

SCRAPER_TOKEN = os.getenv("THORDATA_SCRAPER_TOKEN")
PUBLIC_TOKEN = os.getenv("THORDATA_PUBLIC_TOKEN")
PUBLIC_KEY = os.getenv("THORDATA_PUBLIC_KEY")

if not SCRAPER_TOKEN:
    raise RuntimeError(
        "THORDATA_SCRAPER_TOKEN is missing. "
        "Please create a .env file at the project root and set your tokens."
    )

client = ThordataClient(
    scraper_token=SCRAPER_TOKEN,
    public_token=PUBLIC_TOKEN,
    public_key=PUBLIC_KEY,
)

# Name visible to the MCP client (e.g. Claude)
mcp = FastMCP("Thordata Tools")

# Map simple engine names to the Engine enum
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
    Convert raw HTML into a cleaned plain-text representation.

    - Removes scripts, styles, navigation, footers, SVGs, iframes.
    - Collapses whitespace and drops empty lines.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove noisy elements
    for tag in soup(["script", "style", "nav", "footer", "svg", "iframe", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    clean_text = "\n".join(lines)
    return clean_text


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
                Defaults to 'google'.
        num: Number of results to retrieve (default: 5).
        location: Optional location string (e.g. 'United States', 'London').
        search_type: Optional search type for engines that support it
                     (e.g. 'shopping', 'news', 'images', 'videos').

    Returns:
        A JSON-formatted string containing:
        {
          "engine": "...",
          "query": "...",
          "results": [
            { "rank": 1, "title": "...", "link": "...", "snippet": "..." },
            ...
          ]
        }
    """
    try:
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
            # For Google this usually maps to tbm / type parameters; we rely on
            # the backend / SDK to forward correctly.
            extra_params["type"] = search_type

        results = client.serp_search(
            query=query,
            engine=engine_enum,
            num=num,
            **extra_params,
        )

        organic: List[Dict] = results.get("organic") or []
        if not organic:
            return json.dumps(
                {"message": "No organic results found.", "engine": engine_key},
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
    except Exception as exc:
        logger.exception("search_web failed: %s", exc)
        return json.dumps(
            {"error": f"Search Error: {exc!s}", "engine": engine},
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
    Convenience wrapper around search_web() to search for **news**.

    Args:
        query: The search keywords.
        engine: Search engine to use (default: 'google').
        num: Number of results to retrieve.
        location: Optional location string.

    Returns:
        Same JSON structure as search_web(), but with search_type='news'.
    """
    # Internally we just call search_web with a fixed search_type
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

    Args:
        url: The target URL.
        js_render: Whether to enable JavaScript rendering (default: True).
        country: Optional country code for geo-targeting (e.g. 'us').
        max_chars: Maximum number of characters to return, to stay within
                   token limits.

    Returns:
        A plain-text representation of the page, truncated for token safety.
    """
    try:
        logger.info(
            "[MCP] read_website -> url=%r, js_render=%s, country=%r, max_chars=%d",
            url,
            js_render,
            country,
            max_chars,
        )

        html = client.universal_scrape(
            url=url,
            js_render=js_render,
            output_format="HTML",
            country=country,
        )

        if not html or len(html) < 100:
            return f"Error: Failed to retrieve content or content is empty. URL: {url}"

        clean_text = clean_html_to_text(html)

        if max_chars and len(clean_text) > max_chars:
            clean_text = clean_text[:max_chars]

        return f"Source: {url}\n\n{clean_text}"
    except Exception as exc:
        logger.exception("read_website failed: %s", exc)
        return f"Scrape Error: {exc!s}"


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
    Extract hyperlinks from the given URL.

    Args:
        url: The target URL.
        js_render: Whether to enable JavaScript rendering (default: False).
        country: Optional country code for geo-targeting.
        max_links: Maximum number of links to return.
        unique: Whether to deduplicate links by their final URL.

    Returns:
        JSON string:
        {
          "source": "...",
          "count": N,
          "links": [
            { "text": "...", "href": "absolute_url" },
            ...
          ]
        }
    """
    try:
        logger.info(
            "[MCP] extract_links -> url=%r, js_render=%s, country=%r, max_links=%d, unique=%s",
            url,
            js_render,
            country,
            max_links,
            unique,
        )

        html = client.universal_scrape(
            url=url,
            js_render=js_render,
            output_format="HTML",
            country=country,
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

            # Resolve relative URLs
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
    except Exception as exc:
        logger.exception("extract_links failed: %s", exc)
        return json.dumps(
            {"source": url, "error": f"Extract Links Error: {exc!s}"},
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