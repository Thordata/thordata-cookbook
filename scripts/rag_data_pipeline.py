"""
RAG Data Pipeline Example

This script demonstrates how to:
1. Use Thordata's Universal Scraping API to fetch a fully rendered web page.
2. Clean the noisy HTML into a Markdown-like text suitable for RAG / LLMs.
3. Save the result to a local file (knowledge_base_sample.md).
"""

import os
from typing import List

from bs4 import BeautifulSoup
from dotenv import load_dotenv

from thordata import ThordataClient  # Note: new import path


# Load environment variables from .env
load_dotenv()


def clean_html_to_markdown(html_content: str) -> str:
    """
    Basic ETL step: convert messy HTML into LLM-friendly Markdown-style text.

    The logic here is intentionally simple and opinionated:
    - Remove scripts, styles, navigation, and other non-content elements.
    - Extract headings (h1–h3) and paragraphs.
    - Skip very short paragraphs that are likely boilerplate.

    Args:
        html_content: Raw HTML string.

    Returns:
        A Markdown-like string containing cleaned text.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # 1. Remove irrelevant tags (ads, navigation, scripts, etc.)
    for tag in soup(["script", "style", "nav", "footer", "iframe", "noscript"]):
        tag.decompose()

    # 2. Collect headings and paragraphs
    markdown_lines: List[str] = []

    # Headings (H1–H3)
    for heading in soup.find_all(["h1", "h2", "h3"]):
        level = int(heading.name[1])
        prefix = "#" * level
        markdown_lines.append(f"\n{prefix} {heading.get_text(strip=True)}\n")

    # Paragraphs
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        # Filter out very short / noisy text
        if len(text) > 20:
            markdown_lines.append(text)

    return "\n".join(markdown_lines)


def main() -> None:
    """Run the RAG data pipeline for a single URL."""
    # 1. Initialize client from environment variables
    scraper_token = os.getenv("THORDATA_SCRAPER_TOKEN")
    public_token = os.getenv("THORDATA_PUBLIC_TOKEN")
    public_key = os.getenv("THORDATA_PUBLIC_KEY")

    if not scraper_token:
        print("❌ Error: .env file not found or THORDATA_SCRAPER_TOKEN is missing.")
        return

    client = ThordataClient(scraper_token, public_token, public_key)

    # 2. Target URL (example: OpenAI research page)
    target_url = "https://openai.com/research/"
    print(f"🚀 Starting RAG pipeline for: {target_url}")

    try:
        # 3. Fetch rendered HTML via Universal API
        print("   Requesting Universal Scraper...")
        html = client.universal_scrape(
            url=target_url,
            js_render=True,          # Enable JS rendering for modern sites
            output_format="HTML",
        )
        print(f"✅ Scrape success. Length: {len(html)} characters")

        # 4. Clean & transform HTML into Markdown-like text
        print("   Cleaning and transforming HTML...")
        markdown_content = clean_html_to_markdown(html)

        # 5. Save result to file
        output_file = "knowledge_base_sample.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"Source: {target_url}\n\n")
            f.write(markdown_content)

        print(f"🎉 Pipeline completed! Data saved to '{output_file}'")
        print("   This file is ready for vector database embedding.")
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")


if __name__ == "__main__":
    main()
