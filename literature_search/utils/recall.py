import os
import re
import json
import pickle
import requests
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple

from literature_search.env import (
    API_KEY,
    RERANKER_MODEL,
    RERANK_TOP_N,
    RERANK_SCORE_THRESHOLD
)


def rerank(query: str, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """使用re-ranker模型对检索结果进行重排序"""
    if not documents:
        return []
        
    url = "https://api.siliconflow.cn/v1/rerank"
    
    # 提取文档文本
    doc_texts = [doc["text"] for doc in documents]
    
    payload = {
        "model": RERANKER_MODEL,
        "query": query,
        "documents": doc_texts,
        "top_n": RERANK_TOP_N,
        "return_documents": False,
        "max_chunks_per_doc": 1024,
        "overlap_tokens": 80
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.request("POST", url, json=payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            if "results" in result:
                # 根据重排序结果重新排序文档
                reranked_docs = []
                for rank_result in result["results"]:
                    idx = rank_result["index"]
                    score = rank_result["relevance_score"]
                    if score >= RERANK_SCORE_THRESHOLD:
                        doc = documents[idx].copy()
                        doc["score"] = score
                        reranked_docs.append(doc)
                return reranked_docs
        print(f"重排序失败: {response.text}")
        return documents
    except Exception as e:
        print(f"重排序时出错: {e}")
        return documents


def text_recall(query: str, chunks: List[Dict[str, Any]], top_n: int = RERANK_TOP_N) -> List[Dict[str, Any]]:
    """全文检索：找到包含查询关键词的chunks"""
    # 将查询分词
    
    query_words = set(re.findall(r'\w+', query.lower()))
    if not query_words:
        return []
    
    # 计算每个chunk包含查询词的数量
    results = []
    for chunk in chunks:
        text = chunk["text"].lower()
        # 计算包含的查询词数量
        match_count = sum(1 for word in query_words if word in text)
        if match_count > 0:
            # 计算匹配分数（匹配词数量 / 查询词总数）
            score = match_count / len(query_words)
            chunk_result = chunk.copy()
            chunk_result["score"] = score
            results.append(chunk_result)
    
    # 按匹配分数排序
    results.sort(key=lambda x: x["score"], reverse=True)
    
    # 返回前top_n个结果
    return results[:top_n]

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """计算两个向量的余弦相似度"""
    # 转换为numpy数组
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    # 计算点积
    dot_product = np.dot(vec1, vec2)
    
    # 计算向量模长
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    
    # 计算余弦相似度
    if norm_vec1 > 0 and norm_vec2 > 0:
        return dot_product / (norm_vec1 * norm_vec2)
    else:
        return 0.0

def vector_recall(query_embedding: List[float], chunks: List[Dict[str, Any]], top_n: int) -> List[Dict[str, Any]]:
    """向量检索：找到与查询向量最相似的chunks"""
    if not query_embedding:
        print("无法获取查询的嵌入向量")
        return []
    
    # 计算余弦相似度
    results = []
    for chunk in chunks:
        if "embedding" in chunk:
            similarity = cosine_similarity(query_embedding, chunk["embedding"])
            chunk_result = chunk.copy()
            chunk_result["score"] = similarity
            results.append(chunk_result)
    
    # 按相似度排序
    results.sort(key=lambda x: x["score"], reverse=True)
    
    # 返回前top_n个结果
    return results[:top_n]

