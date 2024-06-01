import csv
import os
import re
import time
import signal
import subprocess
import platform
import csv
import pathlib
import re
import threading
from bs4 import BeautifulSoup
import requests
import json
import ast
from multiprocessing import Pool, TimeoutError
from urllib import parse

def save_to_file(file_name, contents):
    fh = open(file_name, 'w')
    fh.write(contents)
    fh.close()

def clear_irc_color(string):
        pattern = r'\x1b(\[.*?[@-~]|\].*?(\x07|\x1b\\))'
        return re.sub(pattern, '', string)

def create_csv(path):
    with open(path,'w') as f:
        csv_write = csv.writer(f)
        csv_head = ["file_bin_path","file_version","file_size","decompile_time","success_code_0","msg"]
        csv_write.writerow(csv_head)

def read_bytecode(path):
    with open(path) as f:
        content = f.read()
    return content

def write_csv(path,file_bin_path,file_version,file_size ,decompile_time,code,msg):
    with open(path,'a+') as f:
        csv_write = csv.writer(f)
        data_row = [file_bin_path,file_version,file_size,decompile_time,code,msg]
        csv_write.writerow(data_row)

def get_solidity_version_dict():
    solidity_version_from_csv = {}
    with open('../../data/bytecode/normal.csv', mode='r') as inp:
        reader = csv.reader(inp)
        solidity_version_from_csv = {rows[0]:rows[1] for rows in reader}  # 构造一个字典
    return solidity_version_from_csv

dict1 = get_solidity_version_dict()

def get_version(bin_runtime_file):
    # ./Decompile/bin-runtime-bytecode_new/05070424a5236b4ef143a6cd7eb82594f9046088_DEEPSHU.sol/Address.bin-runtime
    # ./mainnet/35/35825b18e8948442abC361B361b007e31130F314_SignedRequest.sol
    # ./Decompile/buggy/runtime/a1.sol/ethBank.bin-runtime
    # ./buggy_dataset/tx7.sol
    l = bin_runtime_file.split("/")
    hash_01 = l[-2][:2]
    # ../../data/sourcecode/mainnet/00/0000000000a84fe7f5d858c8a22121c975ff0b42_Poster.sol
    sol_path = "../../data/sourcecode/mainnet/" + hash_01.lower() + "/" + l[-2]  # 得到文件路径
    result = ast.literal_eval(dict1[sol_path])   # result就是item
    return result["version"]


# ../../data/bytecode/normal_bin-runtime.csv
def get_code(bin_runtime_file):
    bytecode = read_bytecode(bin_runtime_file) # 读取二进制文件
    file_version = get_version(bin_runtime_file) # 读取文件版本
    file_size = os.path.getsize(bin_runtime_file) # 读取文件大小
    l = bin_runtime_file.split("/")
    save_path = ""
    for i in range(0,len(l)-1):
        save_path = save_path+l[i]+"/"    # 得到上级目录的路径
    save_file_name = l[-1].split(".")[0]+"_onlinedecompiler.txt" 
    HEADERS = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8', 'Key': '332213fa4a9d4288b5668ddd9'}
    # 定义了一个 HTTP 请求的头部信息，包括内容类型和一个键值对
    url = "https://ethervm.io/decompile"
    # 指定了 EtherVM 网站的反编译服务的 URL
    # html = requests.get(url)
    fn = save_path + save_file_name # 最终保存文件的路径
    FormData = {"bytecode": bytecode, "submit":''}
    data = parse.urlencode(FormData)
    # 请求方式 发送 POST 请求到 EtherVM 网站的反编译服务，并将结果存储在 html 变量中
    html = requests.post(url=url, headers=HEADERS, data=data,timeout=120) #
    print(html)
    if html.status_code == 200:
        bs = BeautifulSoup(html.text)
        users = bs.find_all("div", class_="code javascript")
        for each in users:
            with open(fn, 'w') as file_obj:
                file_obj.write(each.text.encode('gbk', 'ignore').decode('gbk'))
        code = 0
        time = html.elapsed.total_seconds()
    else:
        code = 1
        time = 0
    write_csv("../../data/csv_file/online_normal.csv",bin_runtime_file,file_version,file_size ,time,code,html.status_code)


def decompile(duplicate_path, res_csv_path):
    create_csv(res_csv_path)
    with open(duplicate_path, 'r', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        cmd_res = []
        for row in reader:
            print(row)
            bin_runtime_file = row['file_path']
            try:
                get_code(bin_runtime_file)
            except:
                write_csv(res_csv_path, bin_runtime_file, "null", "null", 120, 1,
                          "TimeoutError")


def get_code_optimize(bin_runtime_file):
    bytecode = read_bytecode(bin_runtime_file)  # 获取字节码
    file_version = get_version(bin_runtime_file) # 获取版本
    file_size = os.path.getsize(bin_runtime_file)
    l = bin_runtime_file.split("/")
    save_path = ""
    for i in range(0,len(l)-1):
        save_path = save_path+l[i]+"/" 
    save_file_name = l[-1].split(".")[0]+"_onlinedecompiler.txt" 
    HEADERS = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8', 'Key': '332213fa4a9d4288b5668ddd9'}
    url = "https://ethervm.io/decompile"
    # html = requests.get(url)
    fn = save_path + save_file_name
    FormData = {"bytecode": bytecode, "submit":''}
    data = parse.urlencode(FormData)
    html = requests.post(url=url, headers=HEADERS, data=data,timeout=120)
    print(html)
    if html.status_code == 200:
        bs = BeautifulSoup(html.text)
        users = bs.find_all("div", class_="code javascript")
        for each in users:
            with open(fn, 'w') as file_obj:
                file_obj.write(each.text.encode('gbk', 'ignore').decode('gbk'))
        code = 0
        time = html.elapsed.total_seconds() 
    else:
        code = 1
        time = 0
    write_csv("./Decompile/csv_file/002online_res_optimize.csv",bin_runtime_file,file_version,file_size ,time,code,html.status_code)


def decompile_optimize(duplicate_path,res_csv_path):
    create_csv(res_csv_path)
    with open(duplicate_path,'r',encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        cmd_res = []
        for row in reader:
            bin_runtime_file = row['file_path']
            cmd_res.append(bin_runtime_file)
    print(len(cmd_res))
    with Pool(processes=15) as pool:
        pool.map(get_code_optimize, cmd_res)

# get_code("../../data/bytecode/normal/0000000000a84fe7f5d858c8a22121c975ff0b42_Poster.sol/Poster.bin-runtime")
decompile("../../data/bytecode/normal_bin-runtime.csv","../../data/csv_file/online_normal.csv")
