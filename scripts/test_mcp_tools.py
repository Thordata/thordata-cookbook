"""
Quick local test for MCP tools without an MCP client.
"""

from __future__ import annotations

import os
import sys
from pprint import pprint


def main() -> int:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    # Import after sys.path adjustment (inside function to satisfy Ruff E402)
    from scripts.mcp_server import extract_links, read_website, search_news, search_web

    # 1. Test web search
    print("\n=== search_web (google) ===")
    result = search_web("Thordata proxy network", engine="google", num=3)
    pprint(result)

    # 2. Test news search
    print("\n=== search_news (google) ===")
    news = search_news("AI data infrastructure", engine="google", num=3)
    pprint(news)

    # 3. Test read_website
    print("\n=== read_website ===")
    text = read_website("https://www.example.com", js_render=False, max_chars=500)
    print(text[:500])

    # 4. Test extract_links
    print("\n=== extract_links ===")
    links_json = extract_links("https://www.example.com", js_render=False, max_links=10)
    pprint(links_json)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
