from bs4 import BeautifulSoup
import pandas as pd
import requests, time, os, random
import re
import fake_useragent

from literature_search.env import (
    CONFIG_PROXY
)

ua = fake_useragent.UserAgent()
proxies = CONFIG_PROXY

def request_url(url):
    """封装请求方法"""
    headers = {"User-Agent": ua.random}
    return requests.get(url, headers=headers, proxies=proxies, timeout=30)

def download_pdf(url, save_path) -> bool:
    """下载 PDF 文件"""
    try:
        response = request_url(url)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            print(f"PDF 已下载到 {save_path}")
            return True
        else:
            print(f"下载失败，状态码: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"下载时发生错误: {e}")
        return False



def download_file(url, save_path) -> bool:
    """下载文件"""
    response = request_url(url)
    response.raise_for_status()
    with open(save_path, 'wb') as f:
        f.write(response.content)


