from bs4 import BeautifulSoup
import pandas as pd
import requests, time, os, random
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from literature_search.utils.http import get as request_url

def sci_download(doi: str, output_dir: str):
    """从Sci-Hub下载论文（支持动态链接解析）"""
    print(f"开始下载: {doi}")

    url = f"https://sci-hub.arizonastockbroker.com/{doi}"

    print(f"请求: {url}")
    try:
        # 请求页面
        req = request_url(url)
        req.raise_for_status()
        soup = BeautifulSoup(req.text, "html.parser")

        # 优先解析按钮中的下载链接
        download_url = None

        
        # 尝试解析按钮
        buttons = soup.find_all('button')
        for btn in buttons:
            onclick_value = btn.get('onclick')
            if onclick_value:
                # 处理 location.href 格式
                match = re.search(r"location.href='(.*?)'", onclick_value)
                if match:
                    raw_url = match.group(1)

                    # 补全双斜杠链接
                    if raw_url.startswith('//'):
                        raw_url = f"https:{raw_url}"

                    # 尝试解析该链接
                    if raw_url.startswith('http'):
                        download_url = raw_url
                        print(f"按钮链接: {download_url}")
                        break

         # 尝试解析 iframe
   
        if not download_url:
            print(f"尝试解析iframe")
            iframe = soup.find('iframe')
            if iframe and iframe.get('src'):
                download_url = iframe.get('src')
                if download_url.startswith('//'):
                    download_url = f"https:{download_url}"
                print(f"iframe链接: {download_url}")

        # 尝试解析 embed 标签
        if not download_url:
            print(f"尝试解析embed")
            article = soup.find('div', id='article')
            if article:
                embed = article.find('embed')
                if embed and embed.get('src'):
                    download_url = embed.get('src')
                    if download_url.startswith('//'):
                        download_url = f"https:{download_url}"
                    print(f"embed链接: {download_url}")

        # 处理重定向，确保获取最终链接
        if download_url:
            download_url = download_url.replace(r"\/", "/")
            res = request_url(download_url)
            res.raise_for_status()

            # 检查最终链接是否指向 PDF
            final_url = res.url
            print(f"开始下载: {final_url}")

            # 生成规范化的文件名
            safe_doi = doi.replace('/', '_').replace(':', '_').replace('?', '_')
            file_name = f"{safe_doi}.pdf" if '.pdf' in final_url or 'application/pdf' in res.headers.get('Content-Type', '') else f"{safe_doi}.bin"
            file_path = os.path.join(output_dir, file_name)

            # 保存文件
            with open(file_path, 'wb') as file:
                file.write(res.content)

            print(f"文件已保存: {file_path}")
        else:
            print(f"未找到下载链接: {doi}")

    except requests.exceptions.Timeout:
        print(f"超时: {doi}")
    except requests.exceptions.ConnectionError:
        print(f"连接失败: {doi}")
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {doi} - {e}")
    except Exception as e:
        print(f"未知错误: {doi} - {e}")

# 下载函数
def sci_download_with_delay(doi, output_dir, min_delay=1.5, max_delay=3):
    """带延迟的下载函数"""
    try:
        sci_download(doi, output_dir)
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    except Exception as e:
        print(f"下载失败: {doi}，错误: {e}")

# 并行下载主函数
def download(doi_path: str, output_dir: str, max_workers=5):
    """并行下载函数"""
    start_time = time.time()

    # 创建保存下载文章的文件夹
    os.makedirs(output_dir, exist_ok=True)

    # 读取CSV文件
    data = pd.read_csv(doi_path)

    # 提取DOI列表
    dois = data['DOI'].dropna().tolist()
    total = len(dois)

    if total == 0:
        print("没有找到DOI，退出！")
        return

    print(f"开始下载 {total} 篇文章，最大并发数：{max_workers}")

    # 并行下载
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(sci_download_with_delay, doi, output_dir) for doi in dois]

    end_time = time.time()
    print(f"下载完成！")
