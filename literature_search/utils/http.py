from threading import local

import requests
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from literature_search.env import CONFIG_PROXY

_worker = local()
_user_agent = UserAgent()


def get(url: str, *, timeout: int = 30, **kwargs) -> requests.Response:
    """在同一下载线程内复用连接，并重试临时错误。"""
    session = getattr(_worker, "session", None)
    if session is None:
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        _worker.session = session

    return session.get(
        url, headers={"User-Agent": _user_agent.random},
        proxies=CONFIG_PROXY, timeout=timeout, **kwargs,
    )
