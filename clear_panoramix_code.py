import csv
import re
import os 

# 用于清除字符串中的 IRC (Internet Relay Chat) 颜色标记
def clear_irc_color(string):
        pattern = r'\x1b(\[.*?[@-~]|\].*?(\x07|\x1b\\))'
        return re.sub(pattern, '', string)

# 用于读取指定路径下的字节码文件并返回其内容
def read_bytecode(path):
    with open(path) as f:
        content = f.read()
    return content

# 用于将给定内容写入到指定的文件中,若该文件不存在则创建该文件
def save_to_file(file_name, contents):
    fh = open(file_name, 'w')
    fh.write(contents)
    fh.close()

# 从指定的文件中读取内容，清除其中的IRC颜色代码，然后将处理后的内容保存回原文件
def panormaix_clear(file_path):
    content  = read_bytecode(file_path)
    content = clear_irc_color(content)
    save_to_file(file_path,content)

# 将读取到的内容包裹在 "contract { \n" 和 "\n }" 中
def add_infor(file_path):
    content  = read_bytecode(file_path)
    content = "contract { \n" + content +"\n }" 
    # content = content.replace('def', 'function')
    # content = content.replace('#', '//')
    save_to_file(file_path,content)

# 由bytecode-file_path得到合约名和hash值，从而得到panoramix.txt的路径，清除IRC并添加contract{}
def delete_all():
    file_name = "../../data/bytecode/normal_bin-runtime.csv"
    i = 0
    with open(file_name,'r',encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            file_path = row['file_path']
            # ../../data/bytecode/normal/0000000000a84fe7f5d858c8a22121c975ff0b42_Poster.sol/Poster.bin-runtime
            l = file_path.split("/")
            contract_name = l[-1].split(".")[0]                 # Poster
            hash_contract_name = l[-2]                         # 0000000000a84fe7f5d858c8a22121c975ff0b42_Poster.sol
            panoramix_res_file = "../../data/bytecode/normal/" + hash_contract_name + "/"+contract_name + "_panoramix.txt"
            if os.path.exists(panoramix_res_file):
                print(i)
                i = i+1
                panormaix_clear(panoramix_res_file)
                add_infor(panoramix_res_file)



def delete_optimize():
    file_name = "./Decompile/csv_file/001_optimize_bin_new_.csv" 
    i = 0
    with open(file_name,'r',encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            file_path = row['file_path']
            l = file_path.split("/")
            contract_name = l[-1].split(".")[0]
            hash_contract_name = l[-2]
            panoramix_res_file = "./Decompile/optimize_new/" + hash_contract_name + "/"+contract_name + "_panoramix.txt"
            if os.path.exists(panoramix_res_file):
                print(i)
                i = i+1
                panormaix_clear(panoramix_res_file)
                add_infor(panoramix_res_file)


def delete_lines(filename, head,tail):
    fin = open(filename, 'r')
    a = fin.readlines()
    fout = open(filename, 'w')
    b = ''.join(a[head:-tail])
    fout.write(b)


def delete_buggy():
    file_name = "./Decompile/buggy/buggy_bin.csv" 
    i = 0
    with open(file_name,'r',encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            file_path = row['file_path']
            l = file_path.split("/")
            contract_name = l[-1].split(".")[0]
            hash_contract_name = l[-2]
            panoramix_res_file = "./Decompile/buggy/runtime/" + hash_contract_name + "/"+contract_name + "_panoramix.txt"
            if os.path.exists(panoramix_res_file):
                print(i)
                i = i+1
                panormaix_clear(panoramix_res_file)
                add_infor(panoramix_res_file)


def add_infor_vandal(file_path):
    content  = read_bytecode(file_path)
    content = "contract { \n" + content +"\n }" 
    # content = content.replace('def', 'function')
    # content = content.replace('#', '//')
    save_to_file(file_path,content)

# 为vandal添加contract{}
def add_vandal():
    file_name = "../../data/bytecode/normal_bin-runtime.csv"
    i = 0
    with open(file_name,'r',encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            file_path = row['file_path']
            l = file_path.split("/")
            contract_name = l[-1].split(".")[0]
            hash_contract_name = l[-2]
            vandal_txt = "../../data/bytecode/normal/" + hash_contract_name + "/"+contract_name + "_vandal.txt"
            if os.path.exists(vandal_txt):
                print(i)
                i = i+1
                add_infor_vandal(vandal_txt)
                # delete_lines(vandal_txt,1,1)


def add_vandal_buggy():
    file_name = "./Decompile/buggy/buggy_bin.csv" 
    i = 0
    with open(file_name,'r',encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            file_path = row['file_path']
            l = file_path.split("/")
            contract_name = l[-1].split(".")[0].split("_")[0]
            hash_contract_name = l[-2]
            vandal_txt = "./Decompile/buggy/runtime/" + hash_contract_name + "/"+contract_name + "_vandal.txt"
            if os.path.exists(vandal_txt):
                print(i)
                i = i+1
                add_infor_vandal(vandal_txt)



delete_all()
# delete_optimize()
# delete_buggy()
add_vandal()
# add_vandal_buggy()

