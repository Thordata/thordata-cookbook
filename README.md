# 🍳 Thordata Cookbook

[![Thordata SDK](https://img.shields.io/badge/SDK-Thordata%20Python-blue?style=flat-square)](https://github.com/Thordata/thordata-python-sdk)
[![License](https://img.shields.io/github/license/Thordata/thordata-cookbook?style=flat-square)](LICENSE)

End-to-end examples, scripts, and notebooks built on top of the [Thordata Python SDK](https://github.com/Thordata/thordata-python-sdk).

These recipes show how to combine:

- Thordata **SERP API** & **Universal Scraper**
- Thordata **Web Scraper API**
- Modern AI tools (OpenAI, LangChain, MCP)
- Data tools (Pandas, BeautifulSoup)

---

## 🧾 Recipe Index

### Built-in Notebooks & Scripts

| Recipe | Type | Description |
|-------|------|-------------|
| **Web Q&A Agent** | Notebook | `notebooks/ai/web_qa_agent_with_thordata.ipynb`<br>Ask questions, search SERP, scrape pages, and let an LLM answer with citations. Supports live & offline modes. |
| **GitHub Repo Intel** | Notebook | `notebooks/devtools/github_repo_intel.ipynb`<br>Use Web Scraper API spiders to collect GitHub repository metadata (stars, forks, issues) and analyze it with Pandas. |
| **OpenAI Research RAG** | Notebook | `notebooks/rag/rag_openai_research.ipynb`<br>Scrape dynamic pages, clean HTML, and export a Markdown knowledge base for RAG systems. |
| **RAG Data Pipeline** | Script | `scripts/rag_data_pipeline.py`<br>CLI version of the RAG preparation pipeline: Scrape → Clean → Markdown, with CLI flags for URL/country/JS rendering. |
| **MCP Tools for LLMs** | Script | `scripts/mcp_server.py`<br>Model Context Protocol (MCP) server exposing `search_web`, `search_news`, `read_website` to Claude Desktop or other LLMs. |

### External Standalone Examples

| Repository | Description |
|------------|-------------|
| **[thordata-web-qa-agent](https://github.com/Thordata/thordata-web-qa-agent)** | A standalone CLI version of the Web Q&A Agent, easy to fork and deploy. |
| **[google-play-reviews-rag](https://github.com/Thordata/google-play-reviews-rag)** | Fetch Google Play reviews via Web Scraper API, build embeddings, and run RAG QA on user feedback. |
| **[google-news-scraper](https://github.com/Thordata/google-news-scraper)** | Specialized CLI for Google News scraping with advanced filtering (topic, publication, time). |

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

---

## 🔐 Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
THORDATA_SCRAPER_TOKEN=your_thordata_scraper_token
THORDATA_PUBLIC_TOKEN=your_thordata_public_token
THORDATA_PUBLIC_KEY=your_thordata_public_key

# Optional: for OpenAI-based recipes
OPENAI_API_KEY=sk-...
```

---

## 🧪 Running Scripts (CLI)

### 1. RAG Data Pipeline

Fetch, clean, and save page content as Markdown:

```bash
python scripts/rag_data_pipeline.py \
  --url "https://openai.com/research" \
  --output "data/openai_research_kb.md" \
  --country "us" \
  --js-render
```

### 2. MCP Server (Claude Tools)

Expose Thordata tools to an MCP client:

```bash
python scripts/mcp_server.py
```

Or test tools locally without a client:

```bash
python -m scripts.test_mcp_tools
```

---

## 📒 Running Notebooks

1. **Activate environment**: 
   ```bash
   source .venv/Scripts/activate
   ```

2. **Start Jupyter**: 
   ```bash
   jupyter lab
   ```

3. **Open a notebook in notebooks/**:
   - `ai/web_qa_agent_with_thordata.ipynb`
   - `devtools/github_repo_intel.ipynb`
   - `rag/rag_openai_research.ipynb`

> **Tip**: Set `USE_LIVE_THORDATA = False` in notebooks to use cached data and save credits during development.

---

## 📂 Structure

```
thordata-cookbook/
├── notebooks/             # Jupyter notebooks by category
│   ├── ai/
│   ├── devtools/
│   └── rag/
├── scripts/               # Standalone Python scripts (CLI / Servers)
│   ├── rag_data_pipeline.py
│   └── mcp_server.py
├── data/                  # Local cache (git-ignored)
├── requirements.txt
├── .env.example
└── README.md
```

---

## 📬 Support

If you have ideas for new recipes, please open an issue or submit a PR!

For SDK-specific questions, visit the [thordata-python-sdk repository](https://github.com/Thordata/thordata-python-sdk).