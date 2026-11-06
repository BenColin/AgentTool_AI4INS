from bs4 import BeautifulSoup
import pandas as pd
import requests, time, os, random

# 文件路径
csv_file_path = 'doi_Scihub.csv'
output_folder = 'PAPER/'


# 创建保存下载文章的文件夹
if not os.path.exists(output_folder):
    os.mkdir(output_folder)
# 读取CSV文件
data = pd.read_csv(csv_file_path)
# 提取DOI列表
dois = data['DOI'].dropna().tolist()


# 设置代理（需要开启翻墙）
proxies = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890",}

# 多种请求头，防止HTTP 403错误
headers_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
]
# 随机选择一个User-Agent
headers={"User-Agent": random.choice(headers_list)}

# 下载文献的函数
def download_paper(doi, output_folder):
    print(f'{doi} is downloading...')
    url = f"https://sci-hub.arizonastockbroker.com/{doi}"
    download_url = None  # 确保变量初始化
    try:
        # 发送请求，并解析HTML
        r = requests.get(url, proxies=proxies, headers=headers, timeout=15)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, "html.parser")

        # 查找下载链接
        minu_div = soup.find('div', id='minu')  # 找到左侧的菜单栏div，里面有想要的下载按钮
        if minu_div:
            buttons_div = minu_div.find('div', id='buttons')  # 查找包含所有按钮的div
            if buttons_div:
                all_buttons = buttons_div.find_all('button')
                download_button = download_button = all_buttons[1]  # 第二个按钮是下载按钮
                if download_button:
                    onclick_value = download_button.get('onclick')
                    print(f"【按钮url】onclick value: {onclick_value}")
                    if onclick_value:
                        # 提取链接部分
                        download_url = onclick_value[15:-1]
                        # 修正链接中的转义字符 - 需要将结果重新赋值给变量
                        download_url = download_url.replace('\/', '/')
                        # 确保所有转义字符都被正确处理
                        download_url = download_url.replace('\\/', '/')
                        print(f"【修正url】download_url: {download_url}")
        
        if download_url:
            print(f"Download URL found: {download_url}")
            # 下载文件
            file_response = requests.get(download_url, proxies=proxies, headers=headers, timeout=15)
            file_response.raise_for_status()

            # 提取文件名
            file_name = doi.replace('/', '_') + '.pdf'
            file_path = os.path.join(output_folder, file_name)

            with open(file_path, 'wb') as f:
                f.write(file_response.content)
            print(f"{doi} downloaded successfully.")
        else:
            print(f"Download URL not found for {doi}.")

    except requests.RequestException as e:
        print(f"Error downloading {doi}: {e}")


# 遍历所有DOI并下载
n=0
for doi in dois:
    n+=1
    download_paper(doi, output_folder)
    if n==3: # 【测试用，实际运行时删除该段】
        break
    time.sleep(random.uniform(1.5, 3))