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
from concurrent.futures import ThreadPoolExecutor, as_completed

def clear_irc_color(string):
    pattern = r'\x1b(\[.*?[@-~]|\].*?(\x07|\x1b\\))'
    return re.sub(pattern, '', string)


# 创建记录反编译后文件路径、反编译时间、成功与否、错误码的文件
def create_csv(path):
    with open(path, 'w') as f:
        csv_write = csv.writer(f)
        csv_head = ["file_bin_path", "file_version", "file_size", "decompile_time", "success_code_0", "msg"]
        csv_write.writerow(csv_head)


# 读取二进制文件（反编译后的文件）
def read_bytecode(path):
    with open(path) as f:
        content = f.read()
    return content


def write_csv(path, file_bin_path, file_version, file_size, decompile_time, code, msg):
    with open(path, 'a+') as f:
        csv_write = csv.writer(f)
        data_row = [file_bin_path, file_version, file_size, decompile_time, code, msg]
        csv_write.writerow(data_row)


def get_solidity_version_dict():
    solidity_version_from_csv = {}
    with open('../../data/bytecode/normal.csv', mode='r') as inp:
        reader = csv.reader(inp)
        solidity_version_from_csv = {rows[0]: rows[1] for rows in reader}  # 构造一个字典
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
    result = ast.literal_eval(dict1[sol_path])  # result就是item
    return result["version"]


# 函数通过调用 subprocess.Popen 来执行命令，并使用 communicate() 方法获取执行结果。
# 如果命令执行超时，则使用 TimeoutExpired 异常进行处理，并终止进程。最后，函数会记录命令执行的时间、返回码以及执行结果，将这些信息写入 CSV 文件中。
def run_cmd(cmd_string, file_path, timeout=120):
    print(cmd_string)
    start_time = time.time()
    p = subprocess.Popen(cmd_string, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True, close_fds=True,
                         start_new_session=True)
    format = 'utf-8'
    code = 0
    msg = "null"
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
    file_version = get_version(file_path)  # 读取文件版本
    file_size = os.path.getsize(file_path)  # 读取文件大小
    write_csv("../../data/csv_file/panoramix_normal.csv", file_path, file_version, file_size, decompile_time, code, msg)


def decompile_task(row, res_csv_path):
    try:
        bin_runtime_file = row['file_path']
        bytecode = read_bytecode(bin_runtime_file)
        l = bin_runtime_file.split("/")
        save_path = "/".join(l[:-1]) + "/"
        save_file_name = l[-1].split(".")[0] + "_panoramix.txt"  # 构建保存文件的名称
        panormaix_cmd = "panoramix " + str(bytecode) + " > " + save_path + save_file_name
        run_cmd(panormaix_cmd, bin_runtime_file)  # 假设这里执行反编译命令
    except Exception as e:
        write_csv(res_csv_path, bin_runtime_file, -1, -1, -1, 1, "Error: " + str(e))

def decompile(duplicate_path, res_csv_path):
    # create_csv(res_csv_path)  # 假设这里创建结果CSV文件
    with open(duplicate_path, 'r', encoding="utf-8") as csvfile:
        reader = list(csv.DictReader(csvfile))  # 将CSV文件的所有行读取到内存中
        with ThreadPoolExecutor(max_workers=15) as executor:
            # 将任务提交给线程池，从指定的行开始
            futures = [executor.submit(decompile_task, row, res_csv_path) for row in reader]
            # 等待所有任务完成
            for future in as_completed(futures):
                # 这里可以处理任务的结果
                pass

# 使用示例

decompile("../../data/bytecode/normal_bin-runtime.csv", "../../data/csv_file/panoramix_normal.csv")


def run_cmd_optimize(cmd_string, file_bin_path, timeout=120):
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
        msg = "[ERROR]Timeout Error : Command '" + file_bin_path + "' timed out after " + str(timeout) + " seconds"
    except Exception as e:
        code = 1
        msg = "[ERROR]Unknown Error : " + str(e)
    end_time = time.time()
    decompile_time = end_time - start_time
    write_csv("../../data/csv_file/panoramix_optimize.csv", file_bin_path, decompile_time, code, msg)


def decompile_optimize(duplicate_path, res_csv_path):
    create_csv(res_csv_path)
    with open(duplicate_path, 'r', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        cmd_res = []
        for row in reader:
            bin_runtime_file = row['file_path']
            l = bin_runtime_file.split("/")
            save_path = "./Decompile/new_file_1017/res"
            save_file_name = l[-1].split(".")[0] + "_panoramix.txt"
            file_path = "./Decompile/bin-runtime-bytecode_new/" + bin_runtime_file
            bytecode = read_bytecode(file_path)
            panormaix_cmd = "panoramix " + str(bytecode) + " > " + save_path
            run_cmd_optimize(panormaix_cmd, bin_runtime_file)

# decompile_optimize("./Decompile/new_file_1017/panaoramix2.csv","../../data/csv_file/panoramix_optimize.csv")

