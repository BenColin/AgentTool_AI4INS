import os
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from literature_search.models.document import Document
from literature_search.utils.embedding import get_embedding, load_all_embeddings
from literature_search.utils.recall import vector_recall, text_recall, rerank


from literature_search.env import (
    RERANK_TOP_N
)

def process_papers(pdf_dir: Path, output_dir: Path, skip_processed: bool = True, max_workers: int = 20) -> bool:
    """并行处理PDF文件，支持可控并发数量"""
    
    if not pdf_dir.exists():
        print(f"pdf_dir: {pdf_dir} 不存在")
        return False
    
    # 获取全部 PDF 文件
    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        print("PAPER目录中没有PDF文件")
        return False
    
    print(f"找到 {len(pdf_files)} 个 PDF 文件")

    # 获取已处理的文件列表
    processed_files = set()
    if skip_processed and output_dir.exists():
        processed_files = {d.name.replace('.pdf', '') for d in output_dir.iterdir() if d.is_dir()}

    # 定义 PDF 处理任务
    def process_pdf(pdf_file: Path):
        if skip_processed and pdf_file.stem in processed_files:
            print(f"跳过已处理文件: {pdf_file.name}")
            return f"跳过: {pdf_file.name}"

        try:
            print(f"处理文件: {pdf_file.name}")
            doc = Document(pdf_file)
            doc.extract_text()
            doc.chunk_text()
            doc.get_embeddings()
            doc.save_embeddings(output_dir=output_dir)
            return f"完成: {pdf_file.name}"

        except Exception as e:
            return f"失败: {pdf_file.name} | 错误: {e}"

    # 并行处理
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_pdf, pdf): pdf for pdf in pdf_files}

        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(result)

    # 显示处理结果
    print("\n 处理完成:")
    for res in results:
        print(res)

    return True

def _hybrid_recall(query: str, chunks: List[Dict[str, Any]], top_n: int) -> List[Dict[str, Any]]:
    """混合检索：结合向量检索和全文检索的结果"""
    
    # 向量检索
    vector_results = vector_recall(get_embedding(query), chunks, top_n * 2)
    
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
        results = rerank(query, results[:top_n * 2])
    
    # 返回前top_n个结果
    return results[:top_n]

def recall(query: str, embedding_dir:str, top_n: int):
    """搜索与查询相关的chunks"""
    # 加载所有嵌入向量
    chunks = load_all_embeddings(embedding_dir)
    if not chunks:
        print("没有找到嵌入向量，请先处理PDF文件")
        return
    
    print(f"\n查询: {query}")
    print(f"已加载{len(chunks)}个chunks用于检索")
    
    # 混合检索
    results = _hybrid_recall(query, chunks, top_n=top_n)
    print(results)
    # 【测试】打印结果
    if results:
        print(f"\n找到{len(results)}个相关chunks:")
        result_list = [
            f"[{i + 1}] 相关度: {result['score']:.4f}\n"
            f"文件: {result['file_name']}\n"
            f"ID: {result['id']}\n"
            f"内容: {result['text'][:800]}..." if len(result['text']) > 200 else f"内容: {result['text']}"
            for i, result in enumerate(results)
        ]
        return result_list
    else:
        print("\n没有找到相关内容")
        return None

    # return [ {title:file_name,  content:text}, {title:file_name,  content:text}]

def main() -> None:
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PDF文档处理和检索系统")
    parser.add_argument("--process", action="store_true", help="处理PAPER文件夹中的PDF文件")
    parser.add_argument("--recall", type=str, help="搜索与查询相关的内容")
    
    args = parser.parse_args()

    # 文件路径配置
    BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
    PAPER_DIR = BASE_DIR / "PAPER"
    EMBEDDING_DIR = BASE_DIR / "EMBEDDING"
    # 确保EMBEDDING在目录内，不存在则创建
    EMBEDDING_DIR.mkdir(exist_ok=True)

    if args.process:
        process_papers(PAPER_DIR, EMBEDDING_DIR)
    elif args.recall:
        recall(args.recall, EMBEDDING_DIR, top_n=RERANK_TOP_N)
    else:
        parser.print_help()
    
    return 200


if __name__ == "__main__":
    main()