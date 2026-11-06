from fastapi import FastAPI, Request, HTTPException
import subprocess

app = FastAPI()

@app.post('/p2')
async def execute_embedding_recall(request: Request):
    # 验证Authorization header
    auth_header = request.headers.get('Authorization')
    if auth_header != 'Bearer YOUR_AUTH_TOKEN':
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
    if func == 'recall':
        cmd = ['python', 'embedding&recall.py', '--recall', detail]
        try:
            # 执行命令并获取输出
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return {
                'status': 'error',
                'errorInfo': f'Command execution failed: {str(e)}',
                'data': None
            }
    elif func == 'process':
        cmd = ['python', 'embedding&recall.py', '--process']
        try:
            # 执行命令并获取输出
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return {
                'status': 'error',
                'errorInfo': f'Command execution failed: {str(e)}',  
            }
    else:
        return {
            'status': 'error',
            'errorInfo': f'Unsupported func: {func}',
            'data': None
        }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=555)