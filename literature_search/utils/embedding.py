import pickle
import requests
from typing import List, Dict, Any


from literature_search.env import (
    API_KEY,
    EMBEDDING_MODEL
)

def get_embedding(text: str) -> List[float]:
    """调用API获取文本的嵌入向量"""
    url = "https://api.siliconflow.cn/v1/embeddings"
    
    payload = {
        "model": EMBEDDING_MODEL,
        "input": text,
        "encoding_format": "float"
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.request("POST", url, json=payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            if "data" in result and len(result["data"]) > 0:
                return result["data"][0]["embedding"]
        print(f"获取嵌入向量失败: {response.text}")
        return None
    except Exception as e:
        print(f"获取嵌入向量时出错: {e}")
        return None
    


def load_all_embeddings(embedding_dir:str) -> List[Dict[str, Any]]:
    """加载所有嵌入向量"""
    all_chunks = []
    
    # 遍历EMBEDDING_DIR下的所有目录
    for file_dir in embedding_dir.iterdir():
        if file_dir.is_dir():
            embedding_file = file_dir / "embeddings.pkl"
            if embedding_file.exists():
                try:
                    with open(embedding_file, 'rb') as f:
                        chunks = pickle.load(f)
                        all_chunks.extend(chunks)
                        print(f"已加载{len(chunks)}个chunks从{embedding_file}")
                except Exception as e:
                    print(f"加载{embedding_file}时出错: {e}")
    
    return all_chunks