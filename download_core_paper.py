from bs4 import BeautifulSoup
import requests, time, os, random, urllib.parse
import pandas as pd
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 文件路径
output_folder = 'path/'  # 下载文件保存的文件夹

# 搜索关键词
search_keyword = "(Electron beam lithography)(Resolution)(Process stability)"  # 指定的搜索关键词
search_page = 1  # 默认搜索第一页
search_sort = 'relevance'  # 默认按相关性排序

# 创建保存下载文章的文件夹
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 如果需要翻墙代理，则启用下面这行，否则赋为None
proxies = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}

# 多种请求头，防止HTTP 403错误
headers_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
]
# 随机选择一个User-Agent
headers = {"User-Agent": random.choice(headers_list)}


def search_and_download_by_keyword(keyword, page=1, sort='relevance'):
    """
    通过关键词搜索并下载文件
    
    Args:
        keyword: 搜索关键词
        page: 页码，默认为1
        sort: 排序方式，默认为relevance
    """
    
    # 构建URL
    encoded_query = urllib.parse.quote(keyword)
    encoded_query = encoded_query.replace('%20', '+')
    url = f"https://core.ac.uk/search/?q={encoded_query}&page={page}&sort={sort}"
    download_url = None
    
    print(f"正在搜索关键词: {keyword}，URL: {url}")
    
    try:
        # 发送请求，并解析HTML
        r = requests.get(url, proxies=proxies, headers=headers, timeout=15, verify=False)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # 查找下载链接
        a_div = soup.find('div', id='__next')  # 找到左侧的菜单栏div，里面有想要的下载按钮
        if a_div:
            b_div = a_div.find('div').find('main').find('div')  # 查找包含所有按钮的div
            if b_div:
                all_div = b_div.find_all('div')
                download_div = all_div[1]  # 第二个按钮是正确路径
                if download_div:
                    c_div = download_div.find('div').find('div').find('div').find('div')
                    if c_div:
                        use_tag = c_div.find('button').find('svg').find('use')
                        if use_tag and use_tag.has_attr('href'):
                            download_url = use_tag['href']
                            print(f"找到use href属性值: {download_url}，正在下载...")
                        else:
                            print("未找到use标签或href属性值")
                    else:
                        print("未找到c_div")
                else:
                    print("未找到download_div")
            else:
                print("未找到b_div")
        else:
            print("未找到a_div")
        
        if download_url:
            print(f"Download URL found: {download_url}")
            # 下载文件
            file_response = requests.get(download_url, proxies=proxies, headers=headers, timeout=15)
            file_response.raise_for_status()

            # 保存文件
            file_name = 'doiTry.csv'
            file_path = os.path.join(output_folder, file_name)
            with open(file_path, 'wb') as file:
                file.write(file_response.content)
            print(f"File saved: {file_path}")
                        
        
