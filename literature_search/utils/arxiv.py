from bs4 import BeautifulSoup
import requests, time, os, random, re
from concurrent.futures import ThreadPoolExecutor, as_completed
from literature_search.utils.download import download_pdf
from literature_search.utils.http import get as http_get

# arxiv search


def search(keyword, num_results=10):
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
        response = http_get(base_url, params=params, timeout=15)

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

def sanitize_filename(filename):
    """处理文件名，移除Windows不允许的特殊字符"""
    # 替换Windows不允许的特殊字符: ? : * " < > | /
    sanitized = re.sub(r'[?:*"<>|/\\]', '-', filename)
    # 将空格替换为下划线
    sanitized = sanitized.replace(" ", "_")
    return sanitized

# 带延迟下载 PDF 文件
def download_with_delay(pdf_url, save_path, min_delay=1.5, max_delay=3):
    """下载 PDF 并添加随机延迟"""
    try:
        download_pdf(pdf_url, save_path)  # 调用你的下载函数
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    except Exception as e:
        print(f"下载失败: {pdf_url}，错误: {e}")

# 并行下载主函数
def download(papers, output_dir: str, max_workers=5):
    """并行下载论文"""
    start_time = time.time()

    # 创建保存文件夹
    os.makedirs(output_dir, exist_ok=True)

    # 构建任务
    futures = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i, paper in enumerate(papers):
            title = paper['title']
            pdf_url = paper['pdf_url']

            # 处理文件名，防止非法字符
            safe_title = sanitize_filename(title)
            
            # 限制文件名长度，防止过长
            save_path = os.path.join(output_dir, f"{safe_title[:50]}_{i+1}.pdf")
            
            # 提交任务
            futures.append(executor.submit(download_with_delay, pdf_url, save_path))

    end_time = time.time()
    print(f"下载完成！")
