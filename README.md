# 🍳 Thordata Cookbook

Practical examples and recipes for building AI data pipelines with **Thordata**.

This repository contains higher-level examples built on top of the
[`thordata-python-sdk`](https://github.com/Thordata/thordata-python-sdk).

---

## Recipes

| Recipe | Description |
| :--- | :--- |
| **[`rag_data_pipeline.py`](rag_data_pipeline.py)** | Scrape any URL into clean Markdown for RAG / vector databases. |
| **[`mcp_server.py`](mcp_server.py)** | Model Context Protocol (MCP) server that gives LLMs access to Google search and web reading via Thordata. |
| **[`notebooks/rag_openai_research.ipynb`](notebooks/rag_openai_research.ipynb)** | RAG pipeline example built from the OpenAI Research page. |

---

### Online vs Offline Mode

Most examples in this cookbook support two modes:

- **Live mode** (`USE_LIVE_THORDATA = True`):  
  The notebook calls Thordata APIs and consumes your credits.
- **Offline mode** (`USE_LIVE_THORDATA = False`):  
  The notebook loads data from a local cache file under `data/`, so you can
  iterate on cleaning and analysis logic without spending credits.

A typical workflow:

1. Set `USE_LIVE_THORDATA = True` and run the fetch cell once to generate
   a cached file (HTML or JSON).
2. Switch back to `USE_LIVE_THORDATA = False` for day‑to‑day development.

---

## Setup

### 1. **Clone the repo**

   ```bash
   git clone https://github.com/Thordata/thordata-cookbook.git
   cd thordata-cookbook
   ```

### Create and activate a virtual environment (recommended)

   ```bash
   python -m venv .venv
   # Linux / macOS
   source .venv/bin/activate
   # Windows
   .venv\Scripts\activate
   ```

### Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

### Configure credentials

   Copy `.env.example` to `.env` and fill in your tokens from the Thordata Dashboard:

   ```bash
   cp .env.example .env   # On Windows: copy .env.example .env
   ```

---

## Usage

### 1. RAG Data Pipeline

Convert a dynamic website into a Markdown knowledge base sample:

```bash
python rag_data_pipeline.py
```

This will:

- Use Thordata's Universal Scraping API to fetch a fully rendered HTML page.
- Clean and transform the HTML into Markdown (simple ETL).
- Save the result to `knowledge_base_sample.md`, ready for embedding into a vector database.

### 2. MCP Server (for LLM Tools)

The `mcp_server.py` script exposes two tools via the
Model Context Protocol (MCP):

- `search_google` – real-time Google search via Thordata SERP API.
- `read_website` – scrape and clean any URL via Thordata Universal API.

To run the MCP server:

```bash
python mcp_server.py
```

Then connect it from a compatible MCP client (e.g. Claude Desktop) by
registering this script as an MCP server.

---

## Notes

- This repository is intentionally example-focused.
- For the core SDK implementation, see
  [thordata-python-sdk](https://github.com/Thordata/thordata-python-sdk).
- Do not commit your `.env` file or any real tokens.