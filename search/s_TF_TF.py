from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
import os, time, random
import urllib.parse

# 多种请求头，防止HTTP 403错误以及其他屏蔽
headers_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
]
user_agent = {"User-Agent": random.choice(headers_list)}

# 设置下载路径（请替换为你想要的路径），创建目录如果不存在
download_path = r"C:\Users\YourUser\Desktop\new\path"
os.makedirs(download_path, exist_ok=True)  # 
# 将下载路径配置到Edge选项
edge_options = Options()
prefs = {
    "download.default_directory": download_path,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}

edge_options.add_argument(f'user-agent={user_agent}')  # 添加随机请求头
edge_options.add_experimental_option("prefs", prefs)  # 添加下载路径配置，只在测试环境中生效


search_format = "(Chemical Vapor Deposition)(CVD)(Magnetic Thin Films)(Microstructure)(Magnetic Properties)"
base_url = "https://www.tandfonline.com/action/doSearch?AllField="

# 对搜索格式进行编码处理
encoded_search = urllib.parse.quote(search_format)
encoded_search = encoded_search.replace("%20", "+")
# 拼接成完整的网页检索格式
web_search_url = base_url + encoded_search
print(web_search_url)
test_url = 'https://core.ac.uk/search/?q=%28Chemical+Vapor+Deposition%29%28CVD%29%28Magnetic+Thin+Films%29%28Microstructure%29%28Magnetic+Properties%29&page=1&sort=relevance'


# 创建WebDriver对象
wd = webdriver.Edge(service=Service(r'D:\edgedriver_win32\msedgedriver.exe'), options=edge_options)
wd.implicitly_wait(5)     # 设置隐式等待时间，每隔0.5s都再次尝试find该元素，直至超过n秒最大时长。

# 打开网页
wd.get(web_search_url)
wd.find_element(By.XPATH, '//*[@id="download-search-results"]').click()

wd.find_element(By.XPATH, '//*[@id="btn-download-search-results"]').click()

# 等待下载完成
time.sleep(2)  # 可以根据实际下载速度调整等待时间

# 等待用户输入后关闭浏览器
input('等待回车键结束程序')