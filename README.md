# Thordata Cookbook

End-to-end examples and notebooks built on top of the
[Thordata Python SDK](https://github.com/Thordata/thordata-python-sdk).

These recipes show how to combine:

- Thordata **SERP API**
- Thordata **Universal Scraper API**
- Thordata **Web Scraper API**
- Modern AI tools (OpenAI, LangChain, MCP)
- Classic data tools (Pandas, BeautifulSoup)

to build practical AI & data pipelines.

---

## 🧾 Recipe Index

| Recipe | Type | Description |
|-------|------|-------------|
| **Web Q&A Agent** | Notebook | `notebooks/ai/web_qa_agent_with_thordata.ipynb` — Ask natural-language questions, search the web via Thordata SERP, scrape pages via Universal Scraper, clean HTML to text, and let an LLM answer with citations. Supports live mode and offline (cached) mode. |
| **GitHub Repo Intelligence** | Notebook | `notebooks/devtools/github_repo_intel.ipynb` — Use Thordata Web Scraper API spiders to collect GitHub repository metadata (stars, forks, issues, contributors, language) and analyze it with Pandas for competitor / portfolio analysis. |
| **OpenAI Research RAG Prep** | Notebook | `notebooks/rag/rag_openai_research.ipynb` — Scrape dynamic pages (e.g. OpenAI Research), clean HTML, and export a Markdown knowledge base suitable for vector databases and RAG systems. |
| **RAG Data Pipeline (script)** | Script | `scripts/rag_data_pipeline.py` — CLI version of the RAG preparation pipeline: Universal Scraper → HTML cleaning → Markdown export, with CLI flags for URL, JS rendering, country, etc. |
| **MCP Tools for LLMs** | Script | `scripts/mcp_server.py` — Model Context Protocol (MCP) server exposing `search_web`, `search_news`, `read_website`, and `extract_links` as tools to LLMs (e.g. Claude Desktop). |
| **MCP Tools Tester** | Script | `scripts/test_mcp_tools.py` — Local test harness to call the MCP tools directly from Python without Claude, useful for debugging and exploration. |

> All recipes assume you have Thordata credentials and (optionally) an OpenAI
> API key configured via `.env` at the project root.

---

## 📦 Installation

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/Thordata/thordata-cookbook.git
cd thordata-cookbook

python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
# source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The requirements.txt includes:

- thordata-sdk — Thordata Python SDK
- python-dotenv — for loading .env
- beautifulsoup4, pandas — HTML cleaning & analysis
- openai — for LLM calls in Web QA / RAG recipes
- mcp / related dependencies — for MCP server (Claude tools)

## 🔐 Configuration

At the root of the repo there is an .env.example. Copy it to .env and fill
in your own credentials:

```bash
cp .env.example .env
Edit .env:
```

```env
THORDATA_SCRAPER_TOKEN=your_thordata_scraper_token
THORDATA_PUBLIC_TOKEN=your_thordata_public_token
THORDATA_PUBLIC_KEY=your_thordata_public_key

# Optional: for OpenAI-based recipes
OPENAI_API_KEY=sk-...

# Optional: MCP-related settings, if needed
MCP_SERVER_PORT=...
```

Notebooks and scripts will automatically load this .env from the project root.

## 🧪 Running the scripts (CLI)

### 1. RAG data pipeline

`scripts/rag_data_pipeline.py` is a command-line tool that:

1. Calls Thordata Universal Scraper to fetch a dynamic HTML page.
2. Cleans it with BeautifulSoup (removing scripts, navigation, etc.).
3. Exports a Markdown knowledge base file for use in RAG systems.

Example:

```bash
python scripts/rag_data_pipeline.py \
  --url "https://openai.com/research" \
  --output "data/openai_research_knowledge_base.md" \
  --country "us" \
  --js-render \
  --block-resources
```

See the script docstring and --help output for all available options.

### 2. MCP server (for Claude / other MCP clients)

`scripts/mcp_server.py` implements an MCP server exposing Thordata-backed tools:

- `search_web` — multi-engine SERP search (Google/Bing/Yandex/DDG), with optional search_type.
- `search_news` — convenience wrapper for news-focused search.
- `read_website` — Universal Scraper + HTML cleaning, returning LLM-friendly text.
- `extract_links` — extract {text, href} link structures from a page.

Run locally:

```bash
python scripts/mcp_server.py
```

Then configure your MCP-capable client (e.g. Claude Desktop) to connect to this
server. The exact configuration depends on the client; see MCP docs for details.

You can test the tools without MCP client using:

```bash
python scripts/test_mcp_tools.py
```

## 📒 Running the notebooks

### Recommended workflow

Start your virtual environment:

```bash
cd thordata-cookbook
.venv\Scripts\activate   # or source .venv/bin/activate
```

Launch Jupyter or JupyterLab:

```bash
jupyter lab
# or
jupyter notebook
```

Open one of the notebooks under notebooks/:

- `ai/web_qa_agent_with_thordata.ipynb`
- `devtools/github_repo_intel.ipynb`
- `rag/rag_openai_research.ipynb`

Each notebook supports:

- **Live mode** — call Thordata APIs and cache results under data/
- **Offline mode** — reuse cached HTML/JSON/Markdown from data/ to avoid
  consuming additional credits during development.

The exact toggle is usually a `USE_LIVE_THORDATA` boolean near the top of
the notebook.

## 📂 Repository structure

```
thordata-cookbook/
  notebooks/
    ai/
      web_qa_agent_with_thordata.ipynb   # Web Q&A Agent (SERP + Universal + LLM)
    devtools/
      github_repo_intel.ipynb            # GitHub repository intelligence
    rag/
      rag_openai_research.ipynb          # RAG-ready knowledge base prep

  scripts/
    rag_data_pipeline.py                 # CLI version of RAG data pipeline
    mcp_server.py                        # MCP server exposing Thordata tools
    test_mcp_tools.py                    # Local tester for MCP tools

  data/                                  # Cached HTML/JSON/Markdown (git-ignored)
  requirements.txt
  .env.example
  .gitignore
  README.md
  LICENSE
```

## 📝 Notes

- **Python version**: The examples are tested primarily on Python 3.10–3.11.
  Newer versions (e.g. 3.12/3.14) may require dependency updates (Pydantic,
  LangChain, etc.).
- **Data privacy**: The data/ directory is git-ignored and intended only for
  local caches. Do not commit real customer data or sensitive crawl outputs.

## 📬 Support & Feedback

If you have ideas for new recipes, or run into issues:

- Open an issue in this repository, or
- Use the [thordata-python-sdk issue tracker](https://github.com/Thordata/thordata-python-sdk/issues)
  if the problem looks SDK-related.

We are especially interested in:

- New AI / RAG / analytics use cases built on top of Thordata
- Integrations with LangChain, MCP, n8n, Airflow, etc.

---