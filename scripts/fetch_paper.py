import arxiv
import json
import os
from datetime import datetime

def fetch_papers():
    # 从环境变量读取搜索类别（如 "cs.AI+cs.LG"）
    category = os.getenv("ARXIV_CATEGORY", "cs.AI+cs.LG+stat.ML")
    max_results = int(os.getenv("MAX_RESULTS", 10))
    
    # 构建查询：按提交日期倒序，限制数量
    client = arxiv.Client()
    search = arxiv.Search(
        query=f"cat:{category}",
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )
    
    papers = []
    for result in client.results(search):
        papers.append({
            "title": result.title,
            "authors": [a.name for a in result.authors],
            "summary": result.summary,
            "pdf_url": result.pdf_url,
            "entry_id": result.entry_id,
            "published": result.published.isoformat()
        })
    
    # 保存为带日期的 JSON 文件
    today = datetime.now().strftime("%Y-%m-%d")
    output_file = f"data/{today}_papers.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(papers)} papers to {output_file}")
    return output_file

if __name__ == "__main__":
    fetch_papers()
