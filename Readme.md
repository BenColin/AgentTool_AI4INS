# Readme

## AUTHOR: 

* 彭科霖

  负责全代码的流程和逻辑的编写

* 王亚男

  进行了部分并行优化和框架梳理

## 环境安装

`pip install -r requirements.txt -U`

### 如果遇到环境异常；提示NoModuleName literature_search

`export PYTHONPATH=/www/wwwroot/literature_search`

`/www/wwwroot/literature_search`是`.env`文件所在的目录

## 启动

`python main.py`  or `uvicorn main:app --host 0.0.0.0 --port 54123 --reload`

## API

url: <http://example.com:54123/proc>

### search

req:

```json
{
    "func" : "search",
    "session": "",
    "detail":"(Chemical Vapor Deposition)(CVD)(Magnetic Thin Films)(Microstructure)(Magnetic Properties)"
}
```

resp:

```json
{ 
    "isSuccess": true, 
    "message": "search", 
    "session": "user_request_r6eiry_5",  
    "data": null 
}
```

### embedding

req:

```json
{
    "func" : "embedding",
    "session": "user_request_r6eiry_5",  
    "detail":""
}
```

resp:

```json
{
    "isSuccess": true,
    "message": "embedding",
    "session": "user_request_r6eiry_5",
    "data": true
}
```

### recall

req:

```json
{
    "func" : "recall",
    "session": "user_request_r6eiry_5",  
    "detail":"(Chemical Vapor Deposition)(CVD)(Magnetic Thin Films)(Microstructure)(Magnetic Properties)"
}
```

resp:

```json
{
    "isSuccess": true,
    "message": "recall",
    "session": "user_request_r6eiry_5",
    "data": [
        "[1] 相关度: 0.8838\n文件: 10.1002_admi.201601185.pdf\nID: 10.1002_admi.201601185.pdf-p1\n内容: www.advmatinterfaces.deFULL PAPER1601185 (1 of 10) © 2017 WILEY-VCH Verlag GmbH & Co. KGaA, Weinheim Combined Macro/Nanoscale Investigation of the Chemical Vapor Deposition of Fe from Fe(CO) 5 Ioannis G. Aviziotis, Thomas Duguet,* Constantin Vahlas, and Andreas G. Boudouvis DOI: 10.1002/admi.201601185molecular compounds have been tested for the deposition of iron compounds containing metalloid and nonmetal ele-ments. It thus appears that the design of precursors for the CVD of pure or alloyed Fe films showed limited progress in recent years. This is in part due to the availability of appropriate precursors for pure Fe deposition, such as the widely used iron pentacarbonyl, Fe(CO) 5. Fe(CO) 5 is highly toxic, flammable, and heat-, air-, and light-sensitive. On the other hand, it is a low co...",
        "[2] 相关度: 0.8242\n文件: 10.1002_admi.201601185.pdf\nID: 10.1002_admi.201601185.pdf-p1-c6\n内容: the deposition temperature. Microstructural characteristics depend on process condi- tions, e.g., deposition temperature, operating pressure, and mass inflow rates. In a previous work, [21] we revealed the effect of the root mean square (RMS), roughness on the electrical resistivity of Al films. Similarly, it has been proven that surface roughness impacts the magnetoresistance and the magnetic properties of thin films through the increase of the in-plane demagnetization factor [22] as well as wetting and bio-properties of surfaces.[23] From this discussion it comes out that the effi- cient control of film properties passes through a consolidated relation between process parameters and films microstructural characteristics, such as the RMS roughness. This can be met through the nanoscale mo...",
        "[3] 相关度: 0.7987\n文件: 10.1002_admi.201601185.pdf\nID: 10.1002_admi.201601185.pdf-p1-c4\n内容: carbon monoxide and decrease of the film roughness when temperature increases. Dr. I. G. Aviziotis, Prof. A. G. Boudouvis School of Chemical EngineeringNational Technical University of AthensHeroon Polytechniou 9, 15780 Zografou, Greece Dr. I. G. Aviziotis, Dr. T. Duguet, Dr. C. Vahlas CIRIMATCNRSUniversité de Toulouse4 allée Emile Monso, BP 44362, 31030 Toulouse cedex 4, FranceE-mail: thomas.duguet@ensiacet.frRoughness Simulation 1. Introduction Iron (Fe) thin films and coatings are involved in a wide spec- trum of advanced applications, for example, for the stabilization of magnetic skyrmions in spintronics technology to produce topologically protected spin textures and electronic states for the transportation and storage of information. [1] They can also be applied as components in magn...",
        "[4] 相关度: 0.4829\n文件: 10.1002_admi.201601185.pdf\nID: 10.1002_admi.201601185.pdf-p1-c1\n内容: www.advmatinterfaces.deFULL PAPER1601185 (1 of 10) © 2017 WILEY-VCH Verlag GmbH & Co. KGaA, Weinheim Combined Macro/Nanoscale Investigation of the Chemical Vapor Deposition of Fe from Fe(CO) 5 Ioannis G. Aviziotis, Thomas Duguet,* Constantin Vahlas, and Andreas G. Boudouvis DOI: 10.1002/admi.201601185molecular compounds have been tested for the deposition of iron compounds containing metalloid and nonmetal ele-ments. It thus appears that the design of precursors for the CVD of pure or alloyed Fe films showed limited progress in recent years. This is in part due to the availability of appropriate precursors for pure Fe deposition, such as the widely used iron pentacarbonyl, Fe(CO) 5. Fe(CO) 5 is highly toxic, flammable, and heat-, air-, and light-sensitive. On the other hand, it is a low co...",
        "[5] 相关度: 0.4223\n文件: 10.1002_admi.201601185.pdf\nID: 10.1002_admi.201601185.pdf-p1-c23\n内容: quantities are calculated along a horizontal line 1 mm above the susceptor and are plotted against the radial distribution from the center of the susceptor. Figure 4. The temperature (left) and the gas velocity (right) profiles inside the reactor during the CVD of Fe from Fe(CO) 5 at T s a) 223 and b) 215 °C. The streamlines added to the velocity profiles show the flow of the mixture inside the reactor. www.advancedsciencenews.com© 2017 WILEY-VCH Verlag GmbH & Co. KGaA, Weinheim 1601185 (7 of 10) www.advmatinterfaces.dethe probability to detach an atom with more than one neigh- bors is negligible.[29] 3. Conclusions The CVD of Fe from Fe(CO) 5 is investigated with the aim to understand and control the behavior of the deposition rate as a function of temperature in the range 130–250 °C and ...",
        "[6] 相关度: 0.3214\n文件: 10.1002_admi.201601185.pdf\nID: 10.1002_admi.201601185.pdf-p1-c10\n内容: stable (90%–91% and 1%–2%, respectively). Similar atomic compositions are also reported by others. [14] The thermal metalorganic chemical vapor deposition (MOCVD) of Fe from Fe(CO) 5 results in rela- tively pure films in which the O and C concentrations are a few at%. [9]2.2. Dependence of the Fe Deposition Rate on Temperature and Pressure Figure 2 presents the Arrhenius plot of the process where both experimental measurements and macroscale computational predictions are shown. In the Arrhenius plot the deposition rate continuously increases with increasing T s up to 180 °C, implying a kinetically limited regime. A transition regime is observed in the range 180–200 °C, where both surface pro- cesses and transport phenomena impact the process. In this range, the deposition rate reaches a pl...",
        "[7] 相关度: 0.2750\n文件: 10.1002_admi.201601185.pdf\nID: 10.1002_admi.201601185.pdf-p1-c31\n内容: partial pressure of CO at the boundary of the surface and k CO is the pre-exponential factor of this process. The latter is fitted to the experimental data as described before, by starting from the dif - fusion-limited regime, where inhibition by CO is more likely. The values of the pre-exponential factors for each reaction are summarized in Table 2. The implementation of the Langmuir–Hinshelwood expression is performed through user defined functions files. [32] 5. Experimental Section Deposition of Fe was performed in a vertical, cylindrical, stagnant flow, cold wall, stainless steel CVD reactor which has been previously described in detail. [21,33] Independent experiments were performed at 13 different T s, in the range 130–250 °C for a fixed pressure of Preactor = 10 Torr and at four di...",
        "[8] 相关度: 0.2672\n文件: 10.1002_admi.201601185.pdf\nID: 10.1002_admi.201601185.pdf-p1-c25\n内容: computational investigation shows that as pressure increases the gas phase decomposition rates increase and the mass diffusion coefficients of Fe(CO) 5 and Fe(CO) 3 decrease. As a result the concentration of these species at the surface decreases and consequently, the deposition rate decreases. Following the macroscopic computational analysis, a multi- scale framework is developed to simulate the surface of Fe films. The framework predicts the RMS measurements with sufficient accuracy but discrepancies exist. The most important of them lie in the range 190–200 °C. In this range, the model shows a monotonous decrease of RMS whereas experimental data show a steep reduction. This discrepancy is attributed to the fact that no information is incorporated in the model con-cerning the morphology ...",
        "[9] 相关度: 0.2420\n文件: 10.1002_admi.201601185.pdf\nID: 10.1002_admi.201601185.pdf-p1-c37\n内容: Cavallotti, A. Barbato, A. Veneroni, J. Cryst. Growth 2004, 206, 371; c) A. Chaterjee, D. G. Vlachos, J. Comput.-Aided Mater. Des. 2007, 14, 253; d) D. T. Gillespie, J. Phys. Chem. 1977, 81, 2340; e) D. T. Gillespie, J. Chem. Phys. 2001, 115, 1716. [25] a) N. Cheimarios, S. Garnelis, G. Kokkoris, A. G. Boudouvis, J. Nanosci. Nanotechnol. 2011, 11, 8132; b) P. D. Christofides, A. Armaou, Y . Lou, A. Varshney, in Control Engineering Series (Ed: W. S. Levine), Birkhäuser, Boston, MA, 2008; c) Y . Lou, P. D. Christofides, Chem. Eng. Sci. 2003, 58, 3115; d) S. T. Rodgers, K. F. Jensen, J. Appl. Phys. 1998, 83, 524. www.advancedsciencenews.com© 2017 WILEY-VCH Verlag GmbH & Co. KGaA, Weinheim 1601185 (10 of 10) www.advmatinterfaces.de Adv. Mater. Interfaces 2017, 1601185[26] M. Masi, V. Bertani, ...",
        "[10] 相关度: 0.2063\n文件: 10.1002_admi.201601185.pdf\nID: 10.1002_admi.201601185.pdf-p1-c3\n内容: to the decrease of the Fe deposition rate. Finally, it has been shown in a recent study [16] that CO molecules impact not only the deposition rate but also the microstructure of the Fe films. The above-mentioned reports do not consider the gas phase whereas it can have a significant effect on the Fe deposition rate. Such information is provided by other authors using infrared spectroscopy [17] and energy-resolved collision-induced Experiments and computations are performed to model the chemical vapor deposition of iron (Fe) from iron pentacarbonyl (Fe(CO) 5). The behavior of the deposition rate is investigated as a function of temperature, in the range 130–250 °C, and pressure in the range 10–40 Torr. Furthermore, the evolu- tion of the surface roughness is correlated with the deposition t..."
    ]
}
```

### finish

req:

```json
{
    "func" : "finish",
    "session": "user_request_r6eiry_5",  
    "detail":"(Chemical Vapor Deposition)(CVD)(Magnetic Thin Films)(Microstructure)(Magnetic Properties)"
}
```

resp:

```json
{
    "isSuccess": true,
    "message": "finish",
    "session": "user_request_r6eiry_5",
    "data": null
}
```

## 需要改进

2、arxiv爬虫的论文爬取去重

当搜到的论文，重整后的标题等于文件夹内某论文标题时，不予下载。

3、外网查询doi的模拟点击

好像单用beautifulsoup解析不足以解决问题了，需要调研该方式

## 处理流程

0、后台挂起DifyTool.py的API服务供agent调用

1、爬取论文

query => search_Scihub_doi.py => download_Scihub_paper.py

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



