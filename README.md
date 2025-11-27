# 🍳 Thordata Cookbook

Practical examples and recipes for building AI data pipelines with **Thordata**.

This repository contains higher‑level examples built on top of the
[`thordata-python-sdk`](https://github.com/Thordata/thordata-python-sdk).

---

## 📚 Recipes

| Recipe | Type | Description |
| :--- | :--- | :--- |
| **[`scripts/rag_data_pipeline.py`](scripts/rag_data_pipeline.py)** | Script (CLI) | Use Thordata's **Universal Scraping API** to fetch any URL and convert it into Markdown, ready for RAG / vector databases. |
| **[`scripts/mcp_server.py`](scripts/mcp_server.py)** | Script (MCP) | **Model Context Protocol (MCP)** server exposing Thordata‑powered tools: web search, news search, web reading, link extraction. |
| **[`notebooks/rag/rag_openai_research.ipynb`](notebooks/rag/rag_openai_research.ipynb)** | Notebook | End‑to‑end RAG pipeline example built from the OpenAI Research page. |
| **[`notebooks/devtools/github_repo_intel.ipynb`](notebooks/devtools/github_repo_intel.ipynb)** | Notebook | DevTools example: collect GitHub repository intelligence (files, stars, issues, forks, language) into a CSV for analysis. |

---

## 🌐 Online vs Offline Mode

Most examples in this cookbook support two modes:

- **Live mode** (`USE_LIVE_THORDATA = True`):  
  The notebook or script calls Thordata APIs and **consumes your credits**.

- **Offline mode** (`USE_LIVE_THORDATA = False`):  
  The notebook loads data from a local cache file under `data/`, so you can
  iterate on cleaning and analysis logic **without spending credits**.

A typical workflow:

1. Set `USE_LIVE_THORDATA = True` and run the "fetch" cell once to generate
   a cached file (HTML or JSON) under `data/`.
2. Switch back to `USE_LIVE_THORDATA = False` for day‑to‑day development.

> Note: The `data/` directory is ignored via `.gitignore` and should not be
> committed to version control.

---

## 🛠 Setup

### 1. Clone the repo

```bash
git clone https://github.com/Thordata/thordata-cookbook.git
cd thordata-cookbook
```

### 2. Create and activate a virtual environment (recommended)

```bash
python -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure credentials

Copy `.env.example` to `.env` and fill in your tokens from the Thordata Dashboard:

```bash
cp .env.example .env   # On Windows: copy .env.example .env
```

You should at least set:

- `THORDATA_SCRAPER_TOKEN`
- `THORDATA_PUBLIC_TOKEN`
- `THORDATA_PUBLIC_KEY`

---

## 🚀 Usage

### 1. RAG Data Pipeline Script

Use the CLI script to turn any web page into a Markdown file ready for RAG.

From the repo root:

```bash
python -m scripts.rag_data_pipeline
```

By default this will:

- Use Thordata's Universal Scraping API to fetch
  https://openai.com/research/ with JS rendering.
- Clean and transform the HTML into Markdown (simple ETL).
- Save the result to `knowledge_base_sample.md`, ready for embedding into
  a vector database.

You can customize the URL and output file, for example:

```bash
python -m scripts.rag_data_pipeline \
  --url https://example.com \
  --output data/example_rag.md \
  --no-js \
  --block-resources
```

Available options (see `scripts/rag_data_pipeline.py` for details):

- `--url` – target URL to scrape
- `--output` – output markdown file path
- `--country` – optional geo‑targeting country (e.g. us)
- `--no-js` – disable JS rendering to speed up simple pages
- `--block-resources` – block heavy resources (images/css) for faster loading

### 2. RAG Notebook (`notebooks/rag/rag_openai_research.ipynb`)

This notebook shows the same idea in an interactive way:

Start JupyterLab from the repo root:

```bash
python -m jupyterlab
```

Open `notebooks/rag/rag_openai_research.ipynb`.

Set `USE_LIVE_THORDATA = True` once to fetch and cache the HTML/markdown.

For normal development, keep `USE_LIVE_THORDATA = False` to work
with the cached data in `data/` or `knowledge_base_sample.md`.

### 3. GitHub Repo Intelligence Notebook

Notebook: `notebooks/devtools/github_repo_intel.ipynb`

This example uses a GitHub Web Scraper spider configured in the Thordata
dashboard to fetch repository intelligence:

- File URLs
- Primary language (`code_language`)
- Issues / PRs / forks / stars
- Last update time, size, etc.

**Workflow:**

1. Make sure you have configured the GitHub spider in the dashboard and
   copied its `spider_id` and `spider_name` into the notebook.

2. In the notebook, set `USE_LIVE_THORDATA = True` once to:
   - Create a Web Scraper task,
   - Poll until completion,
   - Download JSON results,
   - Cache them into `data/github_repo_intel_sample.json`.

3. Switch back to `USE_LIVE_THORDATA = False` for day‑to‑day analysis:
   - The notebook will load the cached JSON from `data/` and build a
     Pandas DataFrame without consuming credits.
   - The cleaned DataFrame is then exported to a CSV (e.g.
     `github_repo_intel_<repo>_<timestamp>.csv`) with rich structure for
     analysis or downstream pipelines.

> If your Web Scraper credits are limited, always keep
> `USE_LIVE_THORDATA = False` once you have a cached JSON sample.

---

## 🔧 MCP Tools

The `scripts/mcp_server.py` file exposes several Thordata-powered tools via the
Model Context Protocol (MCP). These tools
can be used from an MCP-compatible client (e.g. Claude Desktop), or called
directly from Python.

### Available tools

#### `search_web(query, engine="google", num=5, location=None, search_type=None)`

Real-time web search via Thordata SERP API.

- `engine`: `"google"` | `"bing"` | `"yandex"` | `"duckduckgo"`
- `search_type`: e.g. `"news"`, `"shopping"`, `"images"`, `"videos"`

#### `search_news(query, engine="google", num=5, location=None)`

Convenience wrapper around `search_web` with `search_type="news"`.

#### `read_website(url, js_render=True, country=None, max_chars=15000)`

Uses Thordata's Universal Scraping API to fetch a fully rendered page and
return cleaned plain text, truncated to `max_chars`.

#### `extract_links(url, js_render=False, country=None, max_links=200, unique=True)`

Extracts hyperlinks (`<a href="...">`) from a page and returns structured JSON:

```json
[{ "text": "...", "href": "absolute_url" }, ...]
```

### Running the MCP server

From the repository root:

```bash
python -m scripts.mcp_server
```

You should see:

```
Thordata MCP Server is running...
```

### Local testing without an MCP client

You can also test the tools directly via Python:

```bash
python -m scripts.test_mcp_tools
```

This script will:

- Call `search_web` and `search_news`
- Fetch and clean a sample page via `read_website`
- Extract links from a page via `extract_links`

---

## 📝 Notes

- This repository is intentionally example-focused.
- For the core SDK implementation, see
  [thordata-python-sdk](https://github.com/Thordata/thordata-python-sdk).
- Do not commit your `.env` file or any real tokens.
- The `data/` directory is for local caches / outputs only and is ignored
  via `.gitignore`.