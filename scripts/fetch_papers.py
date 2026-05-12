import arxiv
import json
import os
import requests
from datetime import datetime

def is_high_impact_paper(paper):
    # 1. 年份判断
    pub_date = datetime.fromisoformat(paper['published'].replace('Z', '+00:00'))
    if pub_date < datetime(2025, 1, 1, tzinfo=timezone.utc):
        print(f"  跳过 {paper['title'][:60]}... 原因：年份不满足（{pub_date.year}）")
        return False

    # 2. 引用量判断（通过 Semantic Scholar API）
    arxiv_id = paper['entry_id'].split('/abs/')[-1]
    url = f"https://api.semanticscholar.org/v1/paper/arXiv:{arxiv_id}"
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code == 200:
            citations = resp.json().get('citationCount', 0)
            if citations < 20:
                print(f"  跳过 {paper['title'][:60]}... 原因：引用量不足（{citations} 次）")
                return False
        else:
            print(f"  跳过 {paper['title'][:60]}... 原因：Semantic Scholar 未收录该论文")
            return False
    except Exception as e:
        print(f"  检查引用量时出错，跳过该论文: {e}")
        return False

    return True

def fetch_papers():
    # 从环境变量读取搜索类别（如 "cs.AI+cs.LG"）
    keyword = os.getenv("PAPER_KEYWORD", "multimodal causal inference")
    max_results = int(os.getenv("MAX_RESULTS", 10))
    
    # 构建查询：按提交日期倒序，限制数量
    client = arxiv.Client()
    keyword = os.getenv("PAPER_KEYWORD", "multimodal causal inference")
    search = arxiv.Search( query=f"abs:'{keyword}'",
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

    papers = [p for p in papers if is_high_impact_paper(p)]
    papers = update_history(papers)
    
    # 保存为带日期的 JSON 文件
    today = datetime.now().strftime("%Y-%m-%d")
    output_file = f"data/{today}_papers.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(papers)} papers to {output_file}")
    return output_file

def update_history(papers):
    history_file = "data/processed_history.txt"
    # 读取已有 ID
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            existing_ids = set(line.strip() for line in f)
    else:
        existing_ids = set()

    new_papers = []
    for p in papers:
        pid = p["entry_id"]
        if pid not in existing_ids:
            new_papers.append(p)

    # 更新历史记录文件，增加今天推送的论文 ID
    with open(history_file, "a") as f:
        for p in new_papers:
            f.write(p["entry_id"] + "\n")

    print(f"去重后剩余 {len(new_papers)} 篇论文")
    return new_papers

if __name__ == "__main__":
    fetch_papers()
