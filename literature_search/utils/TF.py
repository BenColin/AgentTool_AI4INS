from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import requests, time, os, random
from io import StringIO
import csv,os, time, glob
import urllib.parse
import fake_useragent

from literature_search.env import (
    CONFIG_PROXY
)

ua = fake_useragent.UserAgent()
proxies = CONFIG_PROXY


def TF(search_param:str, driver_path:str, save_path:str):
    os.makedirs(save_path, exist_ok=True)  # 
    # 将下载路径配置到Edge选项
    edge_options = Options()
    prefs = {
        "download.default_directory": save_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }

    edge_options.add_argument(f'user-agent={ ua.random }')  # 添加随机请求头
    edge_options.add_experimental_option("prefs", prefs)  # 添加下载路径配置，只在测试环境中生效

    # search_param = "(Chemical Vapor Deposition)(CVD)(Magnetic Thin Films)(Microstructure)(Magnetic Properties)"
    base_url = "https://www.tandfonline.com/action/doSearch?AllField="

    # 对搜索格式进行编码处理
    encoded_search = urllib.parse.quote(search_param)
    encoded_search = encoded_search.replace("%20", "+")
    # 拼接成完整的网页检索格式
    web_search_url = base_url + encoded_search
    print(web_search_url)
    test_url = 'https://core.ac.uk/search/?q=%28Chemical+Vapor+Deposition%29%28CVD%29%28Magnetic+Thin+Films%29%28Microstructure%29%28Magnetic+Properties%29&page=1&sort=relevance'

    # 创建WebDriver对象
    wd = webdriver.Edge(service=Service(driver_path), options=edge_options)
    wd.implicitly_wait(5)     # 设置隐式等待时间，每隔0.5s都再次尝试find该元素，直至超过n秒最大时长。

    # 打开网页
    wd.get(web_search_url)
    wd.find_element(By.XPATH, '//*[@id="download-search-results"]').click()

    wd.find_element(By.XPATH, '//*[@id="btn-download-search-results"]').click()

    # 等待下载完成
    time.sleep(2)  # 可以根据实际下载速度调整等待时间

def download(search_param:str, driver_path:str, save_path:str):
    os.makedirs(save_path, exist_ok=True)  # 
    # 将下载路径配置到Edge选项
    edge_options = Options()
    prefs = {
        "download.default_directory": save_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }

    edge_options.add_argument(f'user-agent={ ua.random }')  # 添加随机请求头
    edge_options.add_experimental_option("prefs", prefs)  # 添加下载路径配置，只在测试环境中生效

    # search_param = "(Chemical Vapor Deposition)(CVD)(Magnetic Thin Films)(Microstructure)(Magnetic Properties)"
    base_url = "https://www.tandfonline.com/action/doSearch?AllField="

    # 对搜索格式进行编码处理
    encoded_search = urllib.parse.quote(search_param)
    encoded_search = encoded_search.replace("%20", "+")
    # 拼接成完整的网页检索格式
    web_search_url = base_url + encoded_search
    print(web_search_url)
    test_url = 'https://core.ac.uk/search/?q=%28Chemical+Vapor+Deposition%29%28CVD%29%28Magnetic+Thin+Films%29%28Microstructure%29%28Magnetic+Properties%29&page=1&sort=relevance'

    # 创建WebDriver对象
    wd = webdriver.Edge(service=Service(driver_path), options=edge_options)
    wd.implicitly_wait(5)     # 设置隐式等待时间，每隔0.5s都再次尝试find该元素，直至超过n秒最大时长。

    # 打开网页
    wd.get(web_search_url)
    wd.find_element(By.XPATH, '//*[@id="download-search-results"]').click()

    wd.find_element(By.XPATH, '//*[@id="btn-download-search-results"]').click()



def process_doi(file_path:str, doi_path:str):
    # 输入和输出文件路径
    # file_path = r"Taylor and Francis search results (24 March 2025).csv"
    # doi_path = r"doi.csv"
    recommend_n = 10

    # 提取推荐行（前十行）的DOI
    dois = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            if count < recommend_n:  # 只处理前十行
                dois.append(row['DOI'])
                count += 1
            else:
                break

    # 检查输出文件是否存在
    if os.path.exists(doi_path):
        # 如果存在，读取现有内容并添加新的DOI
        existing_dois = []
        with open(doi_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames and 'DOI' in reader.fieldnames:
                for row in reader:
                    existing_dois.append(row['DOI'])
            else:
                # 如果文件存在但没有DOI列，则创建一个空列表
                existing_dois = []
        
        # 去重：只添加不在现有列表中的DOI
        new_dois = []
        for doi in dois:
            if doi not in existing_dois:
                new_dois.append(doi)
                existing_dois.append(doi)  # 更新现有DOI列表，避免重复添加
        
        # 写入合并后的DOI
        with open(doi_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['DOI'])
            writer.writeheader()
            for doi in existing_dois:
                writer.writerow({'DOI': doi})
        
        print(f"已将{len(new_dois)}个新DOI添加到{doi_path}，跳过了{len(dois) - len(new_dois)}个重复DOI")
    else:
        # 如果文件不存在，创建新文件并写入DOI
        with open(doi_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['DOI'])
            writer.writeheader()
            for doi in dois:
                writer.writerow({'DOI': doi})
        
        os.remove(file_path)
        print(f"已在{doi_path}并写入{len(dois)}个DOI")

# if __name__ == "__main__":
#     TF(driver_path=r'D:\edgedriver_win32\msedgedriver.exe', save_path='C:\Users\YourUser\Desktop\new\path')