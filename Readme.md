## 需要改进

2、arxiv爬虫的论文爬取去重

当搜到的论文，重整后的标题等于文件夹内某论文标题时，不予下载。

3、外网查询doi的模拟点击绕过cloudflare



## 处理流程

0、后台挂起DifyTool.py的API服务供agent调用

1、爬取论文

query => search_Scihub_doi.py（search文件夹里） => download_Scihub_paper.py

query => search&download_Arxiv_paper.py

2、将PAPER文件夹中论文库进行文本嵌入，处理后供后续检索

embedding&recall.py --process

3、recall检索

embedding&recall.py --search "你的问题填在这里"



## 论文DOI号爬取

测试案例：(Electron beam lithography)(Resolution)(Process stability)

[(Electron beam lithography)(Resolution)(Process stability) | Page 1 | Search Results | AIP Advances | AIP Publishing](https://pubs.aip.org/aip/adv/search-results?page=1&q=(Electron beam lithography)(Resolution)(Process stability)&fl_SiteID=1000003)

[Search CORE](https://core.ac.uk/search/?q=(Electron+beam+lithography)(Resolution)(Process+stability)&page=1&sort=relevance)

CORE好用

[Search results | Taylor & Francis Online](https://www.tandfonline.com/action/doSearch?AllField=(Electron+beam+lithography)(Resolution)(Process+stability))

Export search results

[(Electron beam lithography)(Resolution)(Process stability) - Search Results - PubMed](https://pubmed.ncbi.nlm.nih.gov/?term=(Electron+beam+lithography)(Resolution)(Process+stability))

一般用于医学界



【难以爬取】

[Articles – DOAJ](https://doaj.org/search/articles?source={"query"%3A{"query_string"%3A{"query"%3A"\\(Electron beam lithography\\)\\(Resolution\\)\\(Process stability\\)"%2C"default_operator"%3A"AND"}}%2C"size"%3A50%2C"sort"%3A[{"created_date"%3A{"order"%3A"desc"}}]%2C"track_total_hits"%3Atrue})

[(Electron beam lithography)(Resolution)(Process stability) - Search | ScienceDirect.com](https://www.sciencedirect.com/search?qs=(Electron beam lithography)(Resolution)(Process stability)&sortBy=relevance)



## 设计思路

'''
我现在希望写一个能实现这样功能的程序：

1、将同目录下PAPER文件夹中pdf文档切分成chunks
使用父子分段模式，父块段落最大长度为500Tokens，分段标识符为\n\n；子块段落最大长度为200tokens，分段标识符为\n。
文本预处理规则为替换掉连续的空格换行符和制表符。

2、使用的text-embedding模型将切分后的chunks进行embedding。然后并保存到同目录下的EMBEDDING文件中，为后续检索做准备。
调用text-embedding模型方式参考如下：
import requests
url = "https://api.siliconflow.cn/v1/embeddings"
API_KEY = "xxxxxc3c-0c6f-4959-bea4-bf6b137xxxxx"
payload = {
    "model": "BAAI/bge-large-m3",
    "input": "Silicon flow embedding online: fast, affordable, and high-quality embedding services. come try it out!",
    "encoding_format": "float"
}
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
response = requests.request("POST", url, json=payload, headers=headers)
print(response.text)

3、使用高质量混合检索从EMBEDDING文件夹进行用户查询，来找到对应PAPER文件夹最相关的4段chunks，最后print出来。
同时执行全文检索（索引文档中的所有词汇，从而允许用户查询任意词汇，并返回包含这些词汇的chunks）；
和向量检索（通过生成查询嵌入并查询与其向量表示最相似的chunks）。
通过调用re-ranker模型，实现根据候选chunks列表与用户问题语义匹配度进行重新排序，从而改进语义排序的结果。
【参数】用户查询的字符串变量名为query，设置"top_n"为4，Score阈值为0.4.
调用re-ranker模型方式参考如下：
import requests
url = "https://api.siliconflow.cn/v1/rerank"
API_KEY = "xxxxxc3c-0c6f-4959-bea4-bf6b137xxxxx"
payload = {
    "model": "BAAI/bge-reranker-v2-m3",
    "query": "Apple",
    "documents": ["apple", "banana", "fruit", "vegetable"],
    "top_n": 4,
    "return_documents": False,
    "max_chunks_per_doc": 1024,
    "overlap_tokens": 80
}
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
response = requests.request("POST", url, json=payload, headers=headers)
print(response.text)
'''









前往

https://core.ac.uk/search/?q=我的问题&page=1&sort=relevance