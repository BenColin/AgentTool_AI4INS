import os
import ast
from pathlib import Path

####################################
# 加载 .env 文件
####################################

BASE_DIR = Path(__file__).parent.parent
print(f"Base directory: {BASE_DIR}")

try:
    from dotenv import find_dotenv, load_dotenv

    # 加载 .env 文件
    env_path = find_dotenv(str(BASE_DIR / ".env"))
    load_dotenv(env_path)
    print(f"Loaded env file: {env_path}")
except ImportError:
    print("dotenv not installed, skipping...")

####################################
# 变量
####################################
HOST = os.environ.get("HOST", "")
PORT = int(os.environ.get("PORT", "54123"))  # 将 PORT 转为整数类型
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "")

# 获取代理配置
CONFIG_PROXY_HTTP = os.environ.get("CONFIG_PROXY_HTTP", "")
CONFIG_PROXY_HTTPS = os.environ.get("CONFIG_PROXY_HTTPS", "")
# 判断并构建字典
CONFIG_PROXY = None
if CONFIG_PROXY_HTTP != "" and CONFIG_PROXY_HTTPS != "":
    CONFIG_PROXY = {}
    if CONFIG_PROXY_HTTP != "":
        CONFIG_PROXY["http"] = CONFIG_PROXY_HTTP
    if CONFIG_PROXY_HTTPS != "":
        CONFIG_PROXY["https"] = CONFIG_PROXY_HTTPS

# embedding 
API_KEY = os.environ.get("API_KEY",'')

# 模型配置
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "")
RERANKER_MODEL = os.environ.get("RERANKER_MODEL", "")

# document 切分参数配置
PARENT_MAX_TOKENS = int(os.environ.get("PARENT_MAX_TOKENS", ""))
CHILD_MAX_TOKENS = int(os.environ.get("CHILD_MAX_TOKENS", ""))
PARENT_DELIMITER = os.environ.get("PARENT_DELIMITER", "")
CHILD_DELIMITER = os.environ.get("CHILD_DELIMITER", "")


# RERANK 检索配置
RERANK_TOP_N = int(os.environ.get("RERANK_TOP_N", "4"))
RERANK_SCORE_THRESHOLD =  int(os.environ.get("RERANK_SCORE_THRESHOLD", "0"))  # 相关度阈值，只返回得分高于此相关度的结果