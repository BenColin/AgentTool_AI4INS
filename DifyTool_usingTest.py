import requests

# 测试本机API对应的URL
url = "http://localhost:555/p2"
# 如果在docker中运行，需要将localhost改为host.docker.internal(因为docker容器本质是虚拟机和宿主机不在同一网络)

# 请求头
headers = {
    "Authorization": "Bearer YOUR_AUTH_TOKEN",
    "Content-Type": "application/json"
}

# 请求体
data = {
    "func": "process",
    "detail": 'aaaa'
}

try:
    # 发送 POST 请求
    response = requests.post(url, headers=headers, json=data)

    # 检查响应状态码
    if response.status_code == 200:
        print("请求成功")
        print(response.text)
    else:
        print(f"请求失败，状态码: {response.status_code}")
        print(response.text)
except requests.RequestException as e:
    print(f"请求发生错误: {e}")