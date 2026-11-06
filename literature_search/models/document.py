import re
import json
import pickle
from pathlib import Path
from typing import List, Dict, Any
from PyPDF2 import PdfReader
from concurrent.futures import ThreadPoolExecutor, as_completed


from literature_search.utils.embedding import get_embedding

# 切分参数配置
from literature_search.env import (
    PARENT_MAX_TOKENS,
    CHILD_MAX_TOKENS,
    PARENT_DELIMITER,
    CHILD_DELIMITER
)



class Document:
    """文档类，用于存储文档信息和内容"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.file_name = file_path.name
        self.content = ""
        self.chunks = []
        self.embeddings = []
        
    def extract_text(self) -> str:
        """从PDF文件中提取并预处理文本"""
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
    
    
    def get_embeddings(self, max_workers: int = 4) -> List[Dict[str, Any]]:
        """为所有 chunks 并行生成嵌入向量"""
        
        if not self.chunks:
            self.chunk_text()

        chunks_with_embeddings = []

        # 定义处理单个 chunk 的逻辑
        def process_chunk(chunk):
            try:
                embedding = get_embedding(chunk["text"])
                if embedding:
                    chunk["embedding"] = embedding
                    return chunk
                else:
                    print(f"无法为 chunk {chunk['id']} 生成嵌入向量")
                    return None
            except Exception as e:
                print(f"处理 chunk {chunk['id']} 时出错: {e}")
                return None

        # 并行处理 chunks
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(process_chunk, chunk): chunk for chunk in self.chunks}

            for future in as_completed(futures):
                result = future.result()
                if result:
                    chunks_with_embeddings.append(result)

        # 将生成的嵌入向量赋值回对象
        self.embeddings = chunks_with_embeddings

        print(f"完成 {len(chunks_with_embeddings)} 个嵌入向量生成")
        
        return chunks_with_embeddings

    def save_embeddings(self, output_dir:str ) -> None:
        """保存嵌入向量到文件"""
        if not self.embeddings:
            self.get_embeddings()
            
        # 创建以文件名为名的目录
        file_dir = output_dir / self.file_name.replace('.pdf', '')
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
