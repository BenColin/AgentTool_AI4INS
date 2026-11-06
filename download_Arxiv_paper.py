import requests
import os, re, time, random
from bs4 import BeautifulSoup

# 设置代理
proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890",
}

# 随机 User-Agent
headers_list = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
]


def fetch_arxiv_results(keyword, num_results=10):
    """从 arXiv 搜索文献"""
    base_url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": keyword,  # "search_query": f"all:{keyword}"
        "start": 0,
        "max_results": num_results,
        "sortBy": "submittedDate",  # 按提交时间排序
        "sortOrder": "descending",  # 降序
    }

    try:
        response = requests.get(base_url, params=params, proxies=proxies, headers={
            "User-Agent": random.choice(headers_list)
        }, timeout=15)

        if response.status_code == 200:
            results = []
            soup = BeautifulSoup(response.content, "xml")
            entries = soup.find_all("entry")
            for entry in entries:
                title = entry.title.text.strip()
                pdf_url = entry.find("link", title="pdf")["href"]
                results.append({"title": title, "pdf_url": pdf_url})
            return results
        else:
            print(f"请求失败，状态码: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
    return []


def download_pdf(url, save_path):
    """下载 PDF 文件"""
    try:
        response = requests.get(url, headers={"User-Agent": random.choice(headers_list)}, proxies=proxies, stream=True, timeout=15)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            print(f"PDF 已下载到 {save_path}")
        else:
            print(f"下载失败，状态码: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"下载时发生错误: {e}")

def sanitize_filename(filename):
    """处理文件名，移除Windows不允许的特殊字符"""
    # 替换Windows不允许的特殊字符: ? : * " < > | /
    sanitized = re.sub(r'[?:*"<>|/\\]', '-', filename)
    # 将空格替换为下划线
    sanitized = sanitized.replace(" ", "_")
    return sanitized

if __name__ == "__main__":
    inp_1 = input("请输入要搜索的关键词，例如(Electron beam lithography)(Resolution)(Process stability)\n")
    # inp_2 = input("请输入要搜索的结果数：")
    inp_2 = 10
    # 【试用】搜索关键词“霍尔效应”和“20”个结果
    keyword = f'all:{inp_1}'
    num_results = inp_2

    # 如果不存在保存目录，则创建保存目录（以前存在arxiv_papers文件夹）
    save_dir = "PAPER"
    os.makedirs(save_dir, exist_ok=True)

    # 获取 arXiv 搜索结果
    papers = fetch_arxiv_results(keyword, num_results=num_results)
    paper_titles = [paper['title'] for paper in papers]
    print(f"共找到{len(papers)}篇论文")
    for i in range(len(paper_titles)):
        print(f"文章 {i} 标题为{paper_titles[i]}")

    #下载每篇论文的 PDF
    for i, paper in enumerate(papers):
        title = paper['title']
        pdf_url = paper['pdf_url']
        safe_title = sanitize_filename(title) # 处理文件名中windows不允许的特殊字符
        save_path = os.path.join(save_dir, f"{safe_title[:50]}_{i+1}.pdf")
        print(f"正在下载: {title}")
        download_pdf(pdf_url, save_path)
        time.sleep(random.uniform(1.5, 3))  # 随机延迟，避免频繁请求

