# input_string = 'workID,"["1_oaiID","2_detail"]","doi","title","["author1","author2"]",createdDate'

def split_custom(input_string):
    # 先将 ,"[ 和 ], 替换为特定分隔符，这里用一个特殊字符组合
    temp_string = input_string.replace(',"[', '|').replace(']",', '|')

    # 按特殊分隔符分割字符串
    parts = temp_string.split('|')
    # print("【test】:",*parts)

    # 对中间的 doi 和 title 部分进行分割
    if len(parts) >= 5:
        middle_parts = parts[2].split(',')
        # 重新组合结果
        result = [parts[0], parts[1]] + middle_parts + [parts[3], parts[4]]
        # print(*result, sep='\n')
        return result
    else:
        # print("字符串分割结果不符合预期")
        return []

if __name__ == "__main__":
    file_path = "results.csv"
    doi_path = "doi.csv"
    recommend_n = 10 # 【【待开发】】
    
    all_list = []
    with open(file_path, 'r', encoding='utf-8') as file:
        n = 0
        for line in file:
            n += 1
            all_list.append(split_custom(line))
        print(f"共处理了{n}条数据")
    doi_list = [sublist[2] for sublist in all_list if (len(sublist) == 6 and sublist[2] != '')]
    print(*doi_list, sep='\n')
    print(f"共读取了{len(doi_list)}个DOI")
    
    # 【第二步】将doi_list添加到doi.csv文件中
    import csv, os
    
    # 读取现有的doi.csv文件内容
    existing_dois = []
    if os.path.exists(doi_path):
        with open(doi_path, 'r', encoding='utf-8') as doi_file:
            reader = csv.reader(doi_file)
            existing_dois = [row for row in reader]
            # print("【test】:",*existing_dois, sep='\n')
    
    # 如果文件为空或不存在，添加标题行
    if not existing_dois:
        existing_dois.append(["DOI"])
    
    # 将新的doi_list添加到现有内容后
    with open(doi_path, 'w', encoding='utf-8', newline='') as doi_file:
        writer = csv.writer(doi_file)
        writer.writerows(existing_dois)  # 写入原有内容
        
        # 将新的DOI添加到文件中，每个DOI作为一行
        for doi in doi_list:
            if doi and doi not in [row[0] for row in existing_dois]:  # 避免重复添加
                writer.writerow([doi])
    
    os.remove(file_path)
    print(f"本次尝试将{len(doi_list)}个DOI添加到doi.csv文件中")
    