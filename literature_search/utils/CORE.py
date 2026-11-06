from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import requests, time, os, random
from io import StringIO
import os, time, glob
import urllib.parse
import fake_useragent
import tempfile, shutil
import psutil
from pathlib import Path

from literature_search.env import (
    CONFIG_PROXY
)

ua = fake_useragent.UserAgent()
proxies = CONFIG_PROXY


def CORE(search_param:str, driver_path:str, save_path:str):
    os.makedirs(save_path, exist_ok=True)  # 
    # 将下载路径配置到Edge选项
    edge_options = Options()
    prefs = {
        "download.default_directory": save_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    edge_options.add_experimental_option("prefs", prefs)

    # 创建WebDriver对象
    wd = webdriver.Edge(service=Service(driver_path), options=edge_options)
    wd.implicitly_wait(5)     # 设置隐式等待时间，每隔0.5s都再次尝试find该元素，直至超过n秒最大时长。
    # 打开网页
    # search_param = "(Chemical Vapor Deposition)(CVD)(Magnetic Thin Films)(Microstructure)(Magnetic Properties)"
    base_url = "https://core.ac.uk/search/?q="

    # 对搜索格式进行编码处理
    encoded_search = urllib.parse.quote(search_param)
    encoded_search = encoded_search.replace("%20", "+")
    # 拼接成完整的网页检索格式
    web_search_url = base_url + encoded_search
    print(web_search_url)

    test_url = 'https://core.ac.uk/search/?q=%28Chemical+Vapor+Deposition%29%28CVD%29%28Magnetic+Thin+Films%29%28Microstructure%29%28Magnetic+Properties%29&page=1&sort=relevance'
    wd.get(web_search_url)
    wd.find_element(By.XPATH, '//*[@id="__next"]/div[1]/main/div/div[2]/div[1]/div[1]/div[1]/div[1]/button').click()

    wd.find_element(By.XPATH, '//*[@id="modal-root"]/div/div[2]/div/div/fieldset/div/div[2]').click()

    wd.find_element(By.XPATH, '//*[@id="modal-root"]/div/div[2]/div/div/footer/button[2]').click()

    # 等待下载完成
    time.sleep(2)  # 可以根据实际下载速度调整等待时间
    # 等待用户输入后关闭浏览器
    # input('等待回车键结束程序')

    '''
    # 获取最新下载的文件并重命名
    list_of_files = glob.glob(os.path.join(download_path, '*.csv'))  # 假设下载的是CSV文件
    if list_of_files:
        latest_file = max(list_of_files, key=os.path.getctime)
        new_filename = os.path.join(download_path, "自定义文件名.csv")
        
        # 如果目标文件已存在，先删除
        if os.path.exists(new_filename):
            os.remove(new_filename)
        
        os.rename(latest_file, new_filename)
        print(f"文件已重命名为: {new_filename}")
    else:
        print("没有找到下载的文件")
    '''


def download(search_param:str, driver_path:str, save_path:str, temp_dir:str):

    # 检查驱动路径
    driver_path = str(Path(driver_path).resolve())  # 转换为绝对路径
    # 创建下载目录（绝对路径）
    save_path = Path(save_path).resolve()
    save_path.mkdir(parents=True, exist_ok=True)

    # 配置 Edge 选项
    edge_options = Options()
    
    # 指定唯一的用户数据目录
    user_data_dir = f'{tempfile.mkdtemp(dir=temp_dir, prefix="edge_profile_")}'
    Path(user_data_dir).mkdir(exist_ok=True)
    
    # 添加稳定性参数
    edge_options.add_argument(f"--user-data-dir={user_data_dir}")
    edge_options.add_argument("--no-sandbox")
    edge_options.add_argument("--disable-dev-shm-usage")
    edge_options.add_argument("--inprivate")  # 启用无痕模式
    edge_options.add_argument("--disable-application-cache")
    edge_options.add_argument("--disk-cache-size=0")
    edge_options.add_argument("--headless=new")          # 关键！启用无头模式
    # 下载配置
    prefs = {
        "download.default_directory": str(save_path),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    edge_options.add_experimental_option("prefs", prefs)

    # 创建 WebDriver
    print(f"准备创建 WebDriver，驱动路径：{driver_path}，用户目录：{user_data_dir}")
    wd = None
    try:
        wd = webdriver.Edge(service=Service(driver_path), options=edge_options)
        print("WebDriver 创建成功")
        # 打开网页
        # search_param = "(Chemical Vapor Deposition)(CVD)(Magnetic Thin Films)(Microstructure)(Magnetic Properties)"
        base_url = "https://core.ac.uk/search/?q="

        # 对搜索格式进行编码处理
        encoded_search = urllib.parse.quote(search_param)
        encoded_search = encoded_search.replace("%20", "+")
        # 拼接成完整的网页检索格式
        web_search_url = base_url + encoded_search
        print(f"打开网页：{web_search_url}")

        wd.get(web_search_url)
        wait = WebDriverWait(wd, 20)
        for xpath in (
            '//*[@id="__next"]/div[1]/main/div/div[2]/div[1]/div[1]/div[1]/div[1]/button',
            '//*[@id="modal-root"]/div/div[2]/div/div/fieldset/div/div[2]',
            '//*[@id="modal-root"]/div/div[2]/div/div/footer/button[2]',
        ):
            wait.until(EC.element_to_be_clickable((By.XPATH, xpath))).click()

        time.sleep(5) 
        # 至此；得到了一个 result.csv
    finally:
        if wd != None :
            wd.quit()  # 确保退出时调用 quit() 而非 close()
        print(f"清理user data dir : {user_data_dir}")
        shutil.rmtree(user_data_dir, ignore_errors=True)  # 关键清理步骤
    '''
    # 获取最新下载的文件并重命名
    list_of_files = glob.glob(os.path.join(download_path, '*.csv'))  # 假设下载的是CSV文件
    if list_of_files:
        latest_file = max(list_of_files, key=os.path.getctime)
        new_filename = os.path.join(download_path, "自定义文件名.csv")
        
        # 如果目标文件已存在，先删除
        if os.path.exists(new_filename):
            os.remove(new_filename)
        
        os.rename(latest_file, new_filename)
        print(f"文件已重命名为: {new_filename}")
    else:
        print("没有找到下载的文件")
    '''


def _split_custom(input_string):
    # 先将 ,"[ 和 ], 替换为特定分隔符，这里用一个特殊字符组合
    temp_string = input_string.replace(',"[', '|').replace(']",', '|')

    # 按特殊分隔符分割字符串
    parts = temp_string.split('|')
    # print("【test】:",*parts)

    # 对中间的 doi 和 title 部分进行分割
    if len(parts) >= 5:
        middle_parts = parts[2].split(',')
        # 重新组合结果
        result = [parts[0], parts[1]] + middle_parts + [parts[3], parts[4]]
        # print(*result, sep='\n')
        return result
    else:
        # print("字符串分割结果不符合预期")
        return []

def process_doi(file_path:str, doi_path:str):
    # 输入和输出文件路径
    # file_path = "results.csv"
    # doi_path = "doi.csv"
    recommend_n = 10 # 【【待开发】】
    
    all_list = []
    with open(file_path, 'r', encoding='utf-8') as file:
        n = 0
        for line in file:
            n += 1
            all_list.append(_split_custom(line))
        print(f"共处理了{n}条数据")
    doi_list = [sublist[2] for sublist in all_list if (len(sublist) == 6 and sublist[2] != '')]
    print(*doi_list, sep='\n')
    print(f"共读取了{len(doi_list)}个DOI")
    
    # 【第二步】将doi_list添加到doi.csv文件中
    import csv, os
    
    # 读取现有的doi.csv文件内容
    existing_dois = []
    if os.path.exists(doi_path):
        with open(doi_path, 'r', encoding='utf-8') as doi_file:
            reader = csv.reader(doi_file)
            existing_dois = [row for row in reader]
            # print("【test】:",*existing_dois, sep='\n')
    
    # 如果文件为空或不存在，添加标题行
    if not existing_dois:
        existing_dois.append(["DOI"])
    
    # 将新的doi_list添加到现有内容后
    with open(doi_path, 'w', encoding='utf-8', newline='') as doi_file:
        writer = csv.writer(doi_file)
        writer.writerows(existing_dois)  # 写入原有内容
        
        # 将新的DOI添加到文件中，每个DOI作为一行
        for doi in doi_list:
            if doi and doi not in [row[0] for row in existing_dois]:  # 避免重复添加
                writer.writerow([doi])
    
    os.remove(file_path)
    print(f"本次尝试将{len(doi_list)}个DOI添加到doi.csv文件中")
    
