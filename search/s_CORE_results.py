from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
import os, time, glob

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
edge_options.add_experimental_option("prefs", prefs)


# 创建WebDriver对象
wd = webdriver.Edge(service=Service(r'D:\edgedriver_win32\msedgedriver.exe'), options=edge_options)
wd.implicitly_wait(5)     # 设置隐式等待时间，每隔0.5s都再次尝试find该元素，直至超过n秒最大时长。
# 打开网页
url = 'https://core.ac.uk/search/?q=%28Chemical+Vapor+Deposition%29%28CVD%29%28Magnetic+Thin+Films%29%28Microstructure%29%28Magnetic+Properties%29&page=1&sort=relevance'
wd.get(url)
wd.find_element(By.XPATH, '//*[@id="__next"]/div[1]/main/div/div[2]/div[1]/div[1]/div[1]/div[1]/button').click()

wd.find_element(By.XPATH, '//*[@id="modal-root"]/div/div[2]/div/div/fieldset/div/div[2]').click()

wd.find_element(By.XPATH, '//*[@id="modal-root"]/div/div[2]/div/div/footer/button[2]').click()

# 等待下载完成
time.sleep(2)  # 可以根据实际下载速度调整等待时间

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

# 等待用户输入后关闭浏览器
input('等待回车键结束程序')