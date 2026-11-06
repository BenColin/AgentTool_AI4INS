from bs4 import BeautifulSoup
import requests, time, os, random, urllib.parse
import pandas as pd

# 文件路径
output_folder = 'paperTry/'  # 下载文件保存的文件夹

# 搜索关键词
search_keyword = "(Electron beam lithography)(Resolution)(Process stability)"  # 指定的搜索关键词
search_page = 1  # 默认搜索第一页
search_sort = 'relevance'  # 默认按相关性排序

# 创建保存下载文章的文件夹
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 多种请求头，防止HTTP 403错误
headers_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
]

# 如果需要翻墙代理，取消下面的注释即可
proxies = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}


def search_and_download_by_keyword(keyword, page=1, sort='relevance'):
    """
    通过关键词搜索并下载文件
    
    Args:
        keyword: 搜索关键词
        page: 页码，默认为1
        sort: 排序方式，默认为relevance
    """
    print(f'正在搜索关键词: {keyword}, 页码: {page}')
    
    # 构建URL
    encoded_query = urllib.parse.quote(keyword)
    url = f"https://core.ac.uk/search/?q={encoded_query}&page={page}&sort={sort}"
    
    print(f"URL: {url}")
    
    # 随机选择一个User-Agent
    headers = {"User-Agent": random.choice(headers_list)}
    
    try:
        # 发送请求，增加重试次数和超时时间
        for retry in range(3):  # 最多重试3次
            try:
                response = requests.get(url, headers=headers, proxies=proxies, timeout=30, verify=False)
                response.raise_for_status()
                break  # 请求成功，跳出重试循环
            except requests.exceptions.RequestException as e:
                print(f"请求失败，正在进行第{retry+1}次重试: {e}")
                if retry == 2:  # 最后一次重试
                    raise  # 重新抛出异常
                time.sleep(2)  # 等待2秒后重试
        
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 尝试多种方式查找下载按钮
        download_buttons = []
        
        # 方法1: 通过类名查找
        buttons1 = soup.select('button.button-button-3fr3r.button-text-2jiil.styles_action-button__1FV1o')
        if buttons1:
            download_buttons.extend(buttons1)
        
        # 方法2: 通过SVG图标查找
        svg_buttons = soup.find_all('button', {'type': 'button'})
        for button in svg_buttons:
            svg = button.find('svg')
            if svg:
                use_tag = svg.find('use')
                if use_tag and 'href' in use_tag.attrs and '#download' in use_tag['href']:
                    download_buttons.append(button)
        
        # 方法3: 通过包含特定文本的按钮查找
        text_buttons = soup.find_all('button')
        for button in text_buttons:
            if button.text and 'download' in button.text.lower():
                download_buttons.append(button)
        
        # 去重
        unique_buttons = []
        for button in download_buttons:
            if button not in unique_buttons:
                unique_buttons.append(button)
        
        download_buttons = unique_buttons
        
        if not download_buttons:
            print("未找到下载按钮，可能网页结构已更改")
            return 0
        
        print(f"找到 {len(download_buttons)} 个下载按钮")
        
        # 处理每个下载按钮
        success_count = 0
        for i, button in enumerate(download_buttons):
            # 找到包含文章信息的父元素
            article_element = find_parent_article(button)
            if not article_element:
                continue
                
            # 提取文章标题
            title_element = article_element.select_one('h2') or article_element.select_one('h3')
            title = title_element.text.strip() if title_element else f"文档_{keyword}_{i+1}"
            
            # 查找文章ID或下载链接
            article_id = extract_article_id(article_element)
            if not article_id:
                continue
                
            # 构建下载链接
            download_url = f"https://core.ac.uk/download/{article_id}"
            
            # 下载文件
            file_name = f"{title}.pdf".replace('/', '_').replace('\\', '_').replace(':', '_')
            file_path = os.path.join(output_folder, file_name)
            
            if download_file(download_url, file_path, headers):
                success_count += 1
            
            # 避免请求过于频繁
            time.sleep(random.uniform(1.5, 3))
        
        print(f"下载完成！成功下载 {success_count} 个文件")
        return success_count
    
    except Exception as e:
        print(f"搜索或下载过程中出错: {e}")
        return 0


def find_parent_article(element):
    """
    查找包含文章信息的父元素
    """
    # 向上查找最多5层父元素
    current = element
    for _ in range(5):
        if not current or current.name == 'body':
            return None
        current = current.parent
        
        # 检查是否是文章元素 - 多种可能的类名
        if current and current.get('class'):
            class_str = ' '.join(current.get('class', []))
            if 'article' in class_str or 'paper' in class_str or 'result' in class_str:
                return current
        
        # 也可能是其他包含文章信息的div
        if current and (current.find('h2') or current.find('h3')):
            return current
    
    return None


def extract_article_id(article_element):
    """
    从文章元素中提取文章ID
    """
    # 尝试从链接中提取ID - 多种可能的链接格式
    link_patterns = ['a[href*="/works/"]', 'a[href*="/download/"]', 'a[href*="/paper/"]']
    
    for pattern in link_patterns:
        links = article_element.select(pattern)
        for link in links:
            href = link.get('href', '')
            
            # 处理不同格式的链接
            if '/works/' in href:
                parts = href.split('/works/')
                if len(parts) > 1:
                    return parts[1].split('/')[0]
            elif '/download/' in href:
                parts = href.split('/download/')
                if len(parts) > 1:
                    return parts[1].split('/')[0]
            elif '/paper/' in href:
                parts = href.split('/paper/')
                if len(parts) > 1:
                    return parts[1].split('/')[0]
    
    # 尝试从其他属性中提取ID
    data_attrs = [attr for attr in article_element.attrs if attr.startswith('data-')]
    for attr in data_attrs:
        if 'id' in attr or 'article' in attr or 'paper' in attr:
            return article_element[attr]
    
    # 尝试从按钮的onclick属性中提取
    buttons = article_element.find_all('button')
    for button in buttons:
        onclick = button.get('onclick')
        if onclick and ('download' in onclick or 'getpdf' in onclick):
            # 尝试提取引号中的内容
            import re
            match = re.search(r'["\']([^"\']*)["\'](\s*\))?', onclick)
            if match:
                return match.group(1)
    
    return None


def download_file(url, filename, headers):
    """
    下载文件
    """
    try:
        print(f"正在下载: {os.path.basename(filename)}")
        print(f"下载链接: {url}")
        
        response = requests.get(url, headers=headers, proxies=proxies, stream=True, timeout=30, verify=False)
        response.raise_for_status()
        
        # 检查内容类型
        content_type = response.headers.get('Content-Type', '')
        if 'application/pdf' not in content_type and 'application/octet-stream' not in content_type:
            print(f"警告: 内容类型不是PDF: {content_type}")
        
        # 保存文件
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"文件已保存: {filename}")
        return True
    
    except Exception as e:
        print(f"下载文件时出错: {e}")
        return False


def download_by_doi(doi):
    """
    通过DOI下载文件
    """
    print(f'正在通过DOI下载: {doi}')
    
    # 尝试通过关键词搜索
    return search_and_download_by_keyword(doi, page=1)


def main():
    """
    主函数
    """
    print("===== Core.ac.uk 文献下载工具 =====\n")
    print(f"使用关键词: {search_keyword}")
    print(f"页码: {search_page}")
    print(f"排序方式: {search_sort}")
    print(f"下载文件将保存到: {output_folder}")
    
    # 直接使用指定的关键词进行搜索和下载
    success_count = search_and_download_by_keyword(search_keyword, search_page, search_sort)
    
    print(f"\n搜索完成！成功下载 {success_count} 个文件到 {output_folder}")


if __name__ == "__main__":
    main()