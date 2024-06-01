import pandas as pd
import csv
import sys


# # 读取CSV文件
# df = pd.read_csv('../../data/csv_file/erays_normal.csv')
#
# # 筛选第一列中字符串以"../../"开头的行
# filtered_df = df[df['file_bin_path'].str.startswith('../../')]
#
# # 将筛选后的数据保存到新的CSV文件
# filtered_df.to_csv('deleted.csv', index=False)


# def count_rows(filename):
#     # 增加CSV字段大小限制
#     csv.field_size_limit(sys.maxsize)
#
#     with open(filename, 'r') as file:
#         reader = csv.reader(file)
#         row_count = sum(1 for row in reader)  # 逐行迭代并计数
#     return row_count
#
# # 调用函数，并替换'yourfile.csv'为你的文件名
# rows = count_rows('../../data/csv_file/panoramix_normal.csv')
# print(f'The file has {rows} rows.')

csv.field_size_limit(sys.maxsize)

def test_csv(path):
    with open(path, 'r', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        i = 0
        for row in reader:
            print(int(row['success_code_0']))
            i = i + 1
        print(" ")
        print(i)

test_csv("../../data/csv_file/panoramix_normal.csv")