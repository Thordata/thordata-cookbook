import os
import time
from thordata_sdk import ThordataClient
from bs4 import BeautifulSoup
from dotenv import load_dotenv # pip install python-dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

def clean_html_to_markdown(html_content):
    """
    简单的 ETL 函数：将杂乱的 HTML 清洗为 AI 易读的 Markdown 格式
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    # 1. 移除无关标签 (广告、导航、脚本)
    for tag in soup(["script", "style", "nav", "footer", "iframe", "noscript"]):
        tag.decompose()
        
    # 2. 提取标题和正文
    markdown_lines = []
    
    # 提取 H1-H6 标题
    for heading in soup.find_all(["h1", "h2", "h3"]):
        prefix = "#" * int(heading.name[1])
        markdown_lines.append(f"\n{prefix} {heading.get_text().strip()}\n")
        
    # 提取段落
    for p in soup.find_all("p"):
        text = p.get_text().strip()
        if len(text) > 20: # 过滤太短的废话
            markdown_lines.append(text)
            
    return "\n".join(markdown_lines)

def main():
    # 1. 初始化客户端
    scraper_token = os.getenv("THORDATA_SCRAPER_TOKEN")
    public_token = os.getenv("THORDATA_PUBLIC_TOKEN")
    public_key = os.getenv("THORDATA_PUBLIC_KEY")
    
    if not scraper_token:
        print("❌ Error: .env file not found or missing tokens.")
        return

    client = ThordataClient(scraper_token, public_token, public_key)
    
    # 2. 设置目标 (以 OpenAI 博客为例，因为很多 AI 公司想抓这个)
    target_url = "https://openai.com/research/" 
    print(f"🚀 Starting RAG Pipeline for: {target_url}")
    
    try:
        # 3. 使用 Universal API 抓取 (自动渲染 JS，绕过反爬)
        print("   Requesting Universal Scraper...")
        html = client.universal_scrape(
            url=target_url,
            js_render=True, # 必须开启，现代网站大多是动态的
            output_format="HTML"
        )
        print(f"✅ Scrape Success! Length: {len(html)} chars")
        
        # 4. 数据清洗 (ETL)
        print("   Processing data...")
        markdown_content = clean_html_to_markdown(html)
        
        # 5. 保存结果
        output_file = "knowledge_base_sample.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"Source: {target_url}\n\n")
            f.write(markdown_content)
            
        print(f"🎉 Pipeline Completed! Data saved to '{output_file}'")
        print("   (This file is ready for Vector Database embedding)")
        
    except Exception as e:
        print(f"❌ Pipeline Failed: {e}")

if __name__ == "__main__":
    main()