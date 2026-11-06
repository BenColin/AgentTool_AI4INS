import pickle
from functools import lru_cache

import requests
from typing import List, Dict, Any


from literature_search.env import (
    API_KEY,
    EMBEDDING_MODEL
)

def get_embedding(text: str) -> List[float] | None:
    """获取嵌入向量，临时失败时返回 None。"""
    try:
        return list(_fetch_embedding(text))
    except Exception as e:
        print(f"获取嵌入向量失败: {e}")
        return None


@lru_cache(maxsize=1024)
def _fetch_embedding(text: str) -> tuple[float, ...]:
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
    
    response = requests.request("POST", url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json().get("data")
    embedding = data[0].get("embedding") if data else None
    if not isinstance(embedding, list) or not embedding:
        raise ValueError("向量接口未返回有效向量")
    return tuple(embedding)
    


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
