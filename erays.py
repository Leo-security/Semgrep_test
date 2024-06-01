import csv
import os
import re
import time
import signal
import subprocess
import platform
import json
import ast
from multiprocessing import Pool, TimeoutError


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


def get_version(bin_runtime_file):
    dict1 = get_solidity_version_dict()
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

def get_solidity_version_dict():
    solidity_version_from_csv = {}
    with open('../../data/bytecode/normal.csv', mode='r') as inp:
        reader = csv.reader(inp)
        solidity_version_from_csv = {rows[0]:rows[1] for rows in reader}  # 构造一个字典
    return solidity_version_from_csv

def run_cmd(cmd_string,timeout=120):
    print(cmd_string)
    file_bin_path = cmd_string.split(" ")[2]
    file_version = get_version(file_bin_path)
    file_size = os.path.getsize(file_bin_path)
    start_time = time.time()
    p = subprocess.Popen(cmd_string, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True, close_fds=True,
                         start_new_session=True)
    format = 'utf-8'
    try:
        (msg, errs) = p.communicate(timeout=timeout)
        ret_code = p.poll()
        if ret_code:
            code = 1
            msg = "[Error]Called Error : " + str(msg.decode(format))
        else:
            code = 0
            msg = str(msg.decode(format))
    except subprocess.TimeoutExpired:
        p.kill()
        p.terminate()
        os.killpg(p.pid, signal.SIGTERM)
        code = 1
        msg = "[ERROR]Timeout Error : Command '" + cmd_string + "' timed out after " + str(timeout) + " seconds"
    except Exception as e:
        code = 1
        msg = "[ERROR]Unknown Error : " + str(e)
    end_time = time.time()
    decompile_time = end_time - start_time
    write_csv("../../data/csv_file/erays_normal.csv",file_bin_path,file_version,file_size ,decompile_time,code,msg)


def run_cmd_optimize(cmd_string,timeout=120):
    print(cmd_string)
    file_bin_path = cmd_string.split(" ")[2]
    file_version = get_version(file_bin_path)
    file_size = os.path.getsize(file_bin_path)
    start_time = time.time()
    p = subprocess.Popen(cmd_string, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True, close_fds=True,
                         start_new_session=True)
    format = 'utf-8'
    try:
        (msg, errs) = p.communicate(timeout=timeout)
        ret_code = p.poll()
        if ret_code:
            code = 1
            msg = "[Error]Called Error : " + str(msg.decode(format))
        else:
            code = 0
            msg = str(msg.decode(format))
    except subprocess.TimeoutExpired:
        p.kill()
        p.terminate()
        os.killpg(p.pid, signal.SIGTERM)
        code = 1
        msg = "[ERROR]Timeout Error : Command '" + cmd_string + "' timed out after " + str(timeout) + " seconds"
    except Exception as e:
        code = 1
        msg = "[ERROR]Unknown Error : " + str(e)
    end_time = time.time()
    decompile_time = end_time - start_time
    write_csv("./Decompile/csv_file/002erays_res_optimize.csv",file_bin_path,file_version,file_size ,decompile_time,code,msg)


def decompile(duplicate_path,res_csv_path):
    create_csv(res_csv_path)
    with open(duplicate_path,'r',encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        cmd_res = []
        for row in reader:
            bin_runtime_file = row['file_path']
            l = bin_runtime_file.split("/")
            save_path = "" 
            for i in range(0,len(l)-1):
                save_path = save_path+l[i]+"/"
            save_file_name = l[-1].split(".")[0]+"erays_res"
            erays_cmd = "python2 ../../decompiler/erays/aggregator.py "+bin_runtime_file+" "+save_path+save_file_name+" -v"
            cmd_res.append(erays_cmd)
            # print(save_path+save_file_name)
    print(len(cmd_res))
    with Pool(processes=15) as pool:
        pool.map(run_cmd, cmd_res)


def decompile_optimize(duplicate_path,res_csv_path):
    create_csv(res_csv_path)
    with open(duplicate_path,'r',encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        cmd_res = []
        for row in reader:
            bin_runtime_file = row['file_path']
            l = bin_runtime_file.split("/")
            save_path = "" 
            for i in range(0,len(l)-1):
                save_path = save_path+l[i]+"/"
            save_file_name = l[-1].split(".")[0]+"erays_res"  
            erays_cmd = "python2 ./erays/aggregator.py "+bin_runtime_file+" "+save_path+save_file_name+" -v"
            cmd_res.append(erays_cmd)
            # print(save_path+save_file_name)
    print(len(cmd_res))
    with Pool(processes=15) as pool:
        pool.map(run_cmd_optimize, cmd_res)

decompile("../../data/bytecode/normal_bin-runtime.csv","../../data/csv_file/erays_normal.csv")
# python2 ../../decompiler/erays/aggregator.py ../../data/bytecode/normal/0000000000a84fe7f5d858c8a22121c975ff0b42_Poster.sol/Poster.bin-runtime ../../data/bytecode/normal/0000000000a84fe7f5d858c8a22121c975ff0b42_Poster.sol/erays_res -v