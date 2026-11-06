from fastapi import FastAPI, Request, HTTPException
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
import os
import subprocess
import uvicorn
import tempfile, shutil
from literature_search.utils import TF, CORE, sci, arxiv
from concurrent.futures import ThreadPoolExecutor, as_completed

from literature_search.env import (
    HOST,
    PORT,
    AUTH_TOKEN,
    RERANK_TOP_N
)

from embedding_and_recall import (
    recall,
    process_papers
)



app = FastAPI()

@app.get('/')
async def get():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

@app.post('/proc')
async def execute_search_embedding_recal(request: Request):
    
    resp = SimpleNamespace(
        isSuccess = False,
        message = "Invalid request",
        session = None,
        data = None
    )

    # 获取请求数据
    request_data = await request.json()

    session = request_data.get('session', None)
    func = request_data.get('func', None)
    detail = request_data.get('detail', None)

    if func == None:
        resp.message = "缺少 func 参数"
        return resp

    if detail == None:
        resp.message = "缺少 detail 参数"
        return resp

    
    # 创建临时文件夹目录
    temp_dir = Path("temp") 
    temp_dir.mkdir(exist_ok=True) 

    # 判断是否需要创建session
    temp_path = None
    if session == None or func == "search":
        if func == "search" :
            # 在 temp_dir 下创建临时目录
            temp_path = Path(tempfile.mkdtemp(dir=temp_dir, prefix="user_request_"))
    else:
        temp_path = "temp" / Path(session)

    if temp_path is None or not Path(temp_path).exists():
        resp.message = "session 不存在"
        return resp


   # 将路径转换为相对路径
    resp.session = str(temp_path.name)
    try:
        ##########################
        # 创建路径和子文件夹
        ##########################
        doi_path = temp_path / "doi.csv"

        download_dir = temp_path / "download"
        download_dir.mkdir(exist_ok=True)

        paper_dir = temp_path / "paper"
        paper_dir.mkdir(exist_ok=True)

        embedding_dir = temp_path / "embedding"
        embedding_dir.mkdir(exist_ok=True)

        resp.message = func
        resp.isSuccess = True
        match func:
            case "search":
                ##########################
                # webbrowser search
                ##########################

                # browser driver
                driver_path = '../driver/msedgedriver'

                # TF / CORE Search
                # TF download 存在登陆问题；临时先不跑
                # tf_download_path = download_dir / "tf"
                # tf_download_path.mkdir(exist_ok=True)
                # TF.download(detail, driver_path=driver_path, save_path=tf_download_path)
                # TF.process_doi()

                print(f"开始core download")
                core_download_path = download_dir / "core"
                core_download_path.mkdir(exist_ok=True)
                print(f"开始core download")
                CORE.download(detail, driver_path=driver_path, save_path=core_download_path, temp_dir=temp_dir)
                print(f"开始process_doi")
                CORE.process_doi(file_path=core_download_path/"results.csv", doi_path=doi_path)

                ##########################
                # download
                ##########################

                # # sci
                # print(f"sci download")
                # sci.download(doi_path=doi_path, output_dir=paper_dir)

                # # arxiv
                # print(f"arxiv download")
                # papers = arxiv.search(detail, 20)
                # arxiv.download(papers=papers, output_dir=paper_dir)

                # 并行

                def sci_task():
                    print(f"\n[Sci] 开始下载...")
                    sci.download(doi_path=doi_path, output_dir=paper_dir)
                    print(f"[Sci] 下载完成！")

                def arxiv_task():
                    print(f"\n[Arxiv] 开始搜索和下载...")
                    papers = arxiv.search(detail, 20)
                    arxiv.download(papers=papers, output_dir=paper_dir)
                    print(f"[Arxiv] 下载完成！")

                # 使用并行处理
                with ThreadPoolExecutor(max_workers=2) as executor:
                    futures = [
                        executor.submit(sci_task),
                        executor.submit(arxiv_task)
                    ]

                    # 等待任务完成
                    for future in as_completed(futures):
                        try:
                            future.result()
                        except Exception as e:
                            resp.isSuccess = False
                            resp.data = str(e)

            case "embedding":
                ##########################
                # embedding
                ##########################
                resp.data = process_papers(pdf_dir=paper_dir, output_dir=embedding_dir, skip_processed=True)
            case "recall":
                ##########################
                # recall
                ##########################
                resp.data = recall(query=detail, embedding_dir=embedding_dir, top_n=RERANK_TOP_N)
            case "finish":
                ##########################
                # finish
                ##########################
                resp.data = shutil.rmtree(temp_path)
    except Exception as e:
        resp.isSuccess = False
        resp.message = f"{func} 发生异常"
        resp.data = str(e)
    
    return resp




@app.post('/p2')
async def execute_embedding_recall(request: Request):
    # 验证Authorization header
    auth_header = request.headers.get('Authorization')
    if auth_header != f'Bearer {AUTH_TOKEN}':
        raise HTTPException(status_code=403, detail="Invalid Authorization header")
    
    # 获取请求数据
    request_data = await request.json()
    func = request_data.get('func', None)
    detail = request_data.get('detail', None)
    
    # 验证参数
    if func is None or detail is None:
        return {
            'status': 'error',
            'errorInfo': 'Missing func or detail parameter',
            'data': None
        }
    
    # 构建命令
    
    # 文件路径配置
    BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
    PAPER_DIR = BASE_DIR / "PAPER"
    EMBEDDING_DIR = BASE_DIR / "EMBEDDING"
    # 确保EMBEDDING在目录内，不存在则创建
    EMBEDDING_DIR.mkdir(exist_ok=True)

    result = None
    match func:
        case 'search':
            search_result = ""
            #  TF / CORE search
        case 'recall':
            if detail is None:
                return {
                    'status': 'error',
                    'errorInfo': 'Missing detail parameter for recall',
                    'data': None
                }
            result =recall(query=detail, embedding_dir=EMBEDDING_DIR, top_n=RERANK_TOP_N)
        case 'embedding':
            result =process_papers(pdf_dir=PAPER_DIR, output_dir=EMBEDDING_DIR, skip_processed=True)
        case _:
            return {
                'status': 'error',
                'errorInfo': f'Unsupported func: {func}',
                'data': None
            }

    # 执行命令并处理异常
    try:
        return {'status': 'success', 'data': result}
    except subprocess.CalledProcessError as e:
        return {
            'status': 'error',
            'errorInfo': f'Command execution failed: {str(e)}',
            'data': None
        }

if __name__ == '__main__':
    print(f"{HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT, reload=True, debug=True)
