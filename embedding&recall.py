import os
import re
import json
import pickle
import requests
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
from PyPDF2 import PdfReader

# API密钥配置***严禁泄露/明码调取！！！
API_KEY = 'YOUR_API_KEY'

# 文件路径配置
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
PAPER_DIR = BASE_DIR / "PAPER"
EMBEDDING_DIR = BASE_DIR / "EMBEDDING"

# 确保EMBEDDING在目录内，不存在则创建
EMBEDDING_DIR.mkdir(exist_ok=True)

# 切分参数配置
PARENT_MAX_TOKENS = 500
CHILD_MAX_TOKENS = 200
PARENT_DELIMITER = "\n\n"
CHILD_DELIMITER = "\n"

# 模型配置
EMBEDDING_MODEL = "BAAI/bge-m3"
RERANKER_MODEL = "BAAI/bge-reranker-v2-m3"

# 检索配置
TOP_N = 4
SCORE_THRESHOLD = 0  # 相关度阈值，只返回得分高于此相关度的结果


class Document:
    """文档类，用于存储文档信息和内容"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.file_name = file_path.name
        self.content = ""
        self.chunks = []
        self.embeddings = []
        
    def extract_text(self) -> str:
        """从PDF文件中预处理文本"""
        try:
            reader = PdfReader(self.file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            # 预处理文本：替换连续的空格、换行符和制表符
            text = re.sub(r'[\s\n\t]+', ' ', text)
            self.content = text
            return text
        except Exception as e:
            print(f"提取文本时出错: {e}")
            return ""
    
    def chunk_text(self) -> List[Dict[str, Any]]:
        """将文本切分为父子块结构"""
        if not self.content:
            self.extract_text()
            
        # 按父块分隔符切分
        parent_chunks = self.content.split(PARENT_DELIMITER)
        
        all_chunks = []
        parent_id = 0
        
        for parent_chunk in parent_chunks:
            # 跳过空白父块
            if not parent_chunk.strip():
                continue
                
            # 如果父块小于最大token数，直接作为一个块
            if len(parent_chunk.split()) <= PARENT_MAX_TOKENS:
                parent_id += 1
                chunk = {
                    "id": f"{self.file_name}-p{parent_id}",
                    "text": parent_chunk,
                    "parent_id": None,
                    "file_name": self.file_name,
                    "is_parent": True
                }
                all_chunks.append(chunk)
                
                # 按子块分隔符切分
                child_chunks = parent_chunk.split(CHILD_DELIMITER)
                child_id = 0
                
                for child_chunk in child_chunks:
                    # 跳过空白子块
                    if not child_chunk.strip():
                        continue
                        
                    # 如果子块小于最大token数，作为子块
                    if len(child_chunk.split()) <= CHILD_MAX_TOKENS:
                        child_id += 1
                        chunk = {
                            "id": f"{self.file_name}-p{parent_id}-c{child_id}",
                            "text": child_chunk,
                            "parent_id": f"{self.file_name}-p{parent_id}",
                            "file_name": self.file_name,
                            "is_parent": False
                        }
                        all_chunks.append(chunk)
            else:
                # 如果父块超过最大token数，按子块分隔符切分
                child_chunks = parent_chunk.split(CHILD_DELIMITER)
                parent_id += 1
                
                # 创建父块（使用前几个子块的内容作为摘要）
                summary = " ".join(child_chunks[:3]) if len(child_chunks) > 3 else parent_chunk
                if len(summary.split()) > PARENT_MAX_TOKENS:
                    summary = " ".join(summary.split()[:PARENT_MAX_TOKENS])
                    
                parent_chunk = {
                    "id": f"{self.file_name}-p{parent_id}",
                    "text": summary,
                    "parent_id": None,
                    "file_name": self.file_name,
                    "is_parent": True
                }
                all_chunks.append(parent_chunk)
                
                # 处理子块
                child_id = 0
                for child_chunk in child_chunks:
                    # 跳过空白子块
                    if not child_chunk.strip():
                        continue
                        
                    # 如果子块超过最大token数，进一步切分
                    words = child_chunk.split()
                    if len(words) > CHILD_MAX_TOKENS:
                        # 按最大token数切分子块
                        for i in range(0, len(words), CHILD_MAX_TOKENS):
                            sub_chunk = " ".join(words[i:i+CHILD_MAX_TOKENS])
                            if sub_chunk.strip():
                                child_id += 1
                                chunk = {
                                    "id": f"{self.file_name}-p{parent_id}-c{child_id}",
                                    "text": sub_chunk,
                                    "parent_id": f"{self.file_name}-p{parent_id}",
                                    "file_name": self.file_name,
                                    "is_parent": False
                                }
                                all_chunks.append(chunk)
                    else:
                        if child_chunk.strip():
                            child_id += 1
                            chunk = {
                                "id": f"{self.file_name}-p{parent_id}-c{child_id}",
                                "text": child_chunk,
                                "parent_id": f"{self.file_name}-p{parent_id}",
                                "file_name": self.file_name,
                                "is_parent": False
                            }
                            all_chunks.append(chunk)
        
        self.chunks = all_chunks
        return all_chunks
    
    def get_embeddings(self) -> List[Dict[str, Any]]:
        """为所有chunks生成嵌入向量"""
        if not self.chunks:
            self.chunk_text()
            
        chunks_with_embeddings = []
        
        for chunk in self.chunks:
            embedding = get_embedding(chunk["text"])
            if embedding:
                chunk["embedding"] = embedding
                chunks_with_embeddings.append(chunk)
            else:
                print(f"无法为chunk {chunk['id']}生成嵌入向量")
        
        self.embeddings = chunks_with_embeddings
        return chunks_with_embeddings
    
    def save_embeddings(self) -> None:
        """保存嵌入向量到文件"""
        if not self.embeddings:
            self.get_embeddings()
            
        # 创建以文件名为名的目录
        file_dir = EMBEDDING_DIR / self.file_name.replace('.pdf', '')
        file_dir.mkdir(exist_ok=True)
        
        # 保存嵌入向量
        embedding_file = file_dir / "embeddings.pkl"
        with open(embedding_file, 'wb') as f:
            pickle.dump(self.embeddings, f)
            
        # 保存元数据（不包含嵌入向量）
        metadata = []
        for chunk in self.embeddings:
            chunk_copy = chunk.copy()
            if "embedding" in chunk_copy:
                del chunk_copy["embedding"]
            metadata.append(chunk_copy)
            
        metadata_file = file_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
            
        print(f"已保存{len(self.embeddings)}个chunks的嵌入向量到{embedding_file}")


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


def rerank_results(query: str, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
        "top_n": TOP_N,
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
                    if score >= SCORE_THRESHOLD:
                        doc = documents[idx].copy()
                        doc["score"] = score
                        reranked_docs.append(doc)
                return reranked_docs
        print(f"重排序失败: {response.text}")
        return documents
    except Exception as e:
        print(f"重排序时出错: {e}")
        return documents


def load_all_embeddings() -> List[Dict[str, Any]]:
    """加载所有嵌入向量"""
    all_chunks = []
    
    # 遍历EMBEDDING_DIR下的所有目录
    for file_dir in EMBEDDING_DIR.iterdir():
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


def vector_recall(query: str, chunks: List[Dict[str, Any]], top_n: int = TOP_N) -> List[Dict[str, Any]]:
    """向量检索：找到与查询向量最相似的chunks"""
    # 获取查询的嵌入向量
    query_embedding = get_embedding(query)
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


def text_recall(query: str, chunks: List[Dict[str, Any]], top_n: int = TOP_N) -> List[Dict[str, Any]]:
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


def hybrid_recall(query: str, chunks: List[Dict[str, Any]], top_n: int = TOP_N) -> List[Dict[str, Any]]:
    """混合检索：结合向量检索和全文检索的结果"""
    # 向量检索
    vector_results = vector_recall(query, chunks, top_n * 2)
    
    # 全文检索
    text_results = text_recall(query, chunks, top_n * 2)
    
    # 合并结果
    combined_results = {}
    
    # 添加向量检索结果
    for result in vector_results:
        combined_results[result["id"]] = result
    
    # 添加全文检索结果，如果已存在则取较高的分数
    for result in text_results:
        if result["id"] in combined_results:
            # 取较高的分数
            if result["score"] > combined_results[result["id"]]["score"]:
                combined_results[result["id"]]["score"] = result["score"]
        else:
            combined_results[result["id"]] = result
    
    # 转换为列表并排序
    results = list(combined_results.values())
    results.sort(key=lambda x: x["score"], reverse=True)
    
    # 使用re-ranker重新排序
    if len(results) > 0:
        results = rerank_results(query, results[:top_n * 2])
    
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


def process_papers(skip_processed: bool = True) -> None:
    """处理PAPER文件夹中的所有PDF文件
    
    Args:
        skip_processed: 是否跳过已处理过的文件。当需要更新模型或重新处理时，设置为False
    """
    # 确保PAPER目录存在
    if not PAPER_DIR.exists():
        print(f"PAPER目录不存在: {PAPER_DIR}")
        return
    
    # 获取所有PDF文件
    pdf_files = list(PAPER_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"PAPER目录中没有PDF文件")
        return
    
    print(f"找到{len(pdf_files)}个PDF文件")
    
    # 获取已处理的文件列表
    processed_files = set()
    if skip_processed and EMBEDDING_DIR.exists():
        processed_files = {d.name.replace('.pdf', '') for d in EMBEDDING_DIR.iterdir() if d.is_dir()}
    
    # 处理每个PDF文件
    for pdf_file in pdf_files:
        # 检查是否已处理
        if skip_processed and pdf_file.stem in processed_files:
            print(f"\n跳过已处理文件: {pdf_file.name}")
            continue
            
        print(f"\n处理文件: {pdf_file.name}")
        doc = Document(pdf_file)
        doc.extract_text()
        doc.chunk_text()
        doc.get_embeddings()
        doc.save_embeddings()


def recall(query: str) -> None:
    """搜索与查询相关的chunks"""
    # 加载所有嵌入向量
    chunks = load_all_embeddings()
    if not chunks:
        print("没有找到嵌入向量，请先处理PDF文件")
        return
    
    print(f"\n查询: {query}")
    print(f"已加载{len(chunks)}个chunks用于检索")
    
    # 混合检索
    results = hybrid_recall(query, chunks, TOP_N)
    
    # 【测试】打印结果
    if results:
        print(f"\n找到{len(results)}个相关chunks:")
        for i, result in enumerate(results):
            print(f"\n[{i+1}] 相关度: {result['score']:.4f}")
            print(f"文件: {result['file_name']}")
            print(f"ID: {result['id']}")
            print(f"内容: {result['text'][:800]}..." if len(result['text']) > 200 else f"内容: {result['text']}")
    else:
        print("\n没有找到相关内容")


def main() -> None:
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PDF文档处理和检索系统")
    parser.add_argument("--process", action="store_true", help="处理PAPER文件夹中的PDF文件")
    parser.add_argument("--recall", type=str, help="搜索与查询相关的内容")
    
    args = parser.parse_args()
    
    if args.process:
        process_papers()
    elif args.recall:
        recall(args.recall)
    else:
        parser.print_help()
    
    return 200


if __name__ == "__main__":
    main()