import json
import os
from datetime import datetime
from google import genai

def call_gemini_summarize(paper):
    """调用 Gemini API 生成结构化精读摘要"""
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    prompt = f"""
请按照以下四个维度对这篇论文进行精读分析：

论文标题：{paper['title']}
论文摘要：{paper['summary']}

1. 目标上下文：这篇论文旨在解决什么“问题”？
2. 与现有工作的对比：它的“出发点”是什么？
3. 核心解决方案/实验：它的“答案”是什么？
4. 文章创新点：它的最大贡献是什么？
"""
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text

def summarize_all():
    today = datetime.now().strftime("%Y-%m-%d")
    input_file = f"data/{today}_papers.json"
    
    with open(input_file, "r", encoding="utf-8") as f:
        papers = json.load(f)
    
    enhanced_papers = []
    for paper in papers:
        print(f"Summarizing: {paper['title']}")
        summary = call_gemini_summarize(paper)
        paper["ai_summary"] = summary
        enhanced_papers.append(paper)
    
    output_file = f"data/{today}_enhanced.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(enhanced_papers, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(enhanced_papers)} summaries to {output_file}")

if __name__ == "__main__":
    summarize_all()
