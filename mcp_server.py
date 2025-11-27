"""
Thordata MCP Server

This script exposes Thordata-powered tools via the Model Context Protocol (MCP):

- search_google(query, num):
    Real-time Google search using Thordata SERP API.
- read_website(url):
    Scrape and clean any web page using the Universal Scraping API.

Intended to be used from an MCP-compatible client (e.g. Claude Desktop).
"""

import os
import json
from pathlib import Path

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from thordata import ThordataClient, Engine  # New import path


# ---------------------------------------------------------------------------
# 1. Load credentials from .env (always relative to this file)
# ---------------------------------------------------------------------------
dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path)

SCRAPER_TOKEN = os.getenv("THORDATA_SCRAPER_TOKEN")
PUBLIC_TOKEN = os.getenv("THORDATA_PUBLIC_TOKEN")
PUBLIC_KEY = os.getenv("THORDATA_PUBLIC_KEY")

if not SCRAPER_TOKEN:
    raise ValueError("Error: Please configure THORDATA_SCRAPER_TOKEN in .env")


# Initialize the Thordata SDK client
client = ThordataClient(SCRAPER_TOKEN, PUBLIC_TOKEN, PUBLIC_KEY)

# ---------------------------------------------------------------------------
# 2. Create MCP server
# ---------------------------------------------------------------------------
# This is the name that will appear to the AI client.
mcp = FastMCP("Thordata Tools")


# ---------------------------------------------------------------------------
# Tool 1: Google Search
# ---------------------------------------------------------------------------
@mcp.tool()
def search_google(query: str, num: int = 5) -> str:
    """
    Use this tool to search Google for real-time information, news, or facts.

    Args:
        query: The search keywords.
        num: Number of results to retrieve (default: 5).

    Returns:
        A JSON-formatted string containing a list of simplified search results.
    """
    try:
        print(f"[MCP] AI is searching Google for: {query}")
        results = client.serp_search(query, engine=Engine.GOOGLE, num=num)

        # Keep only the fields that are useful to the AI client
        clean_results = []
        if "organic" in results:
            for item in results["organic"]:
                clean_results.append(
                    {
                        "title": item.get("title"),
                        "link": item.get("link"),
                        "snippet": item.get("snippet"),
                    }
                )
            return json.dumps(clean_results, ensure_ascii=False, indent=2)
        return "No organic results found."
    except Exception as e:
        return f"Search Error: {str(e)}"


# ---------------------------------------------------------------------------
# Tool 2: Read & Clean Web Page
# ---------------------------------------------------------------------------
@mcp.tool()
def read_website(url: str) -> str:
    """
    Use this tool to read the content of a specific URL.

    This is useful for:
    - Summarizing articles or documentation.
    - Extracting relevant text from dynamic sites.

    Args:
        url: The target URL.

    Returns:
        A plain-text representation of the page, truncated for token safety.
    """
    try:
        print(f"[MCP] AI is reading: {url}")
        # Use Universal API to get rendered HTML
        html = client.universal_scrape(url, js_render=True)

        if not html or len(html) < 100:
            return "Error: Failed to retrieve content or content is empty."

        soup = BeautifulSoup(html, "html.parser")

        # Remove noisy elements
        for tag in soup(["script", "style", "nav", "footer", "svg", "iframe"]):
            tag.decompose()

        # Extract text with line breaks
        text = soup.get_text(separator="\n")

        # Normalize and remove empty lines
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = "\n".join(lines)

        # Truncate to avoid hitting token limits
        max_chars = 15000
        truncated = clean_text[:max_chars]

        return f"Source: {url}\n\n{truncated}"
    except Exception as e:
        return f"Scrape Error: {str(e)}"


# ---------------------------------------------------------------------------
# 3. Run the MCP server
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Thordata MCP Server is running...")
    mcp.run()