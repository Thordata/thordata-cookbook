"""
Quick local test for MCP tools without an MCP client.
"""
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pprint import pprint

from scripts.mcp_server import search_web, search_news, read_website, extract_links


def main():
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


if __name__ == "__main__":
    main()