import csv, os

# 输入和输出文件路径
file_path = r"Taylor and Francis search results (24 March 2025).csv"
doi_path = r"doi.csv"
recommend_n = 10

# 提取推荐行（前十行）的DOI
dois = []
with open(file_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    count = 0
    for row in reader:
        if count < recommend_n:  # 只处理前十行
            dois.append(row['DOI'])
            count += 1
        else:
            break

# 检查输出文件是否存在
if os.path.exists(doi_path):
    # 如果存在，读取现有内容并添加新的DOI
    existing_dois = []
    with open(doi_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames and 'DOI' in reader.fieldnames:
            for row in reader:
                existing_dois.append(row['DOI'])
        else:
            # 如果文件存在但没有DOI列，则创建一个空列表
            existing_dois = []
    
    # 去重：只添加不在现有列表中的DOI
    new_dois = []
    for doi in dois:
        if doi not in existing_dois:
            new_dois.append(doi)
            existing_dois.append(doi)  # 更新现有DOI列表，避免重复添加
    
    # 写入合并后的DOI
    with open(doi_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['DOI'])
        writer.writeheader()
        for doi in existing_dois:
            writer.writerow({'DOI': doi})
    
    print(f"已将{len(new_dois)}个新DOI添加到{doi_path}，跳过了{len(dois) - len(new_dois)}个重复DOI")
else:
    # 如果文件不存在，创建新文件并写入DOI
    with open(doi_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['DOI'])
        writer.writeheader()
        for doi in dois:
            writer.writerow({'DOI': doi})
    
    os.remove(file_path)
    print(f"已在{doi_path}并写入{len(dois)}个DOI")