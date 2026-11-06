from pathlib import Path
from tempfile import NamedTemporaryFile

import requests

from literature_search.utils.http import get as request_url


def download_pdf(url, save_path) -> bool:
    """流式下载 PDF，完整接收后再替换目标文件。"""
    target = Path(save_path)
    partial = None
    try:
        with request_url(url, stream=True) as response:
            if response.status_code != 200:
                print(f"下载失败，状态码: {response.status_code}")
                return False
            with NamedTemporaryFile(dir=target.parent, delete=False) as f:
                partial = Path(f.name)
                for chunk in response.iter_content(chunk_size=65536):
                    f.write(chunk)
        partial.replace(target)
        print(f"PDF 已下载到 {save_path}")
        return True
    except (requests.exceptions.RequestException, OSError) as e:
        print(f"下载时发生错误: {e}")
        return False
    finally:
        if partial is not None:
            partial.unlink(missing_ok=True)



def download_file(url, save_path) -> bool:
    """下载文件"""
    response = request_url(url)
    response.raise_for_status()
    with open(save_path, 'wb') as f:
        f.write(response.content)


