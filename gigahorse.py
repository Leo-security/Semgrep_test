import json
import subprocess
from multiprocessing import Pool, TimeoutError
from pathlib3x import Path

TARGET_FOLDER = Path("../../data/bytecode/normal")
OUTPUT_FOLDER = Path("../../data/bytecode/gigahorse_result/success")
ERROR_FOLDER = Path("../../data/bytecode/gigahorse_result/error")
GIGA = "../../decompiler/gigahorse-toolchain/gigahorse.py"
ARGS = ["--restart", "--disable_inline", "--jobs 8"]
TIMEOUT = 2400

# --restart --disable_inline --jobs 8

def run(sol_file: Path):
    if not any(sol_file.iterdir()):
        print(f"{sol_file}  is empty")
        return

    file_name = sol_file.name
    output_file = OUTPUT_FOLDER / f"{file_name}.json"
    cmd = f"{GIGA} {' '.join(ARGS)} -r {output_file} {sol_file}"  # gigahorse命令

    err = None

    try:
        cp = subprocess.run(cmd, timeout=TIMEOUT, shell=True, capture_output=True)
    except TimeoutError as e:
        err = {"file": file_name, "error": "timeout", "message": "timeout"}
        print(f"{sol_file} timeout")
    except Exception as e:
        err = {"file": file_name, "error": "exception", "message": str(e)}
        print(f"{sol_file} exception")
    else:
        if cp.returncode != 0:
            err = {"file": file_name, "error": "exception", "message": str(cp.stdout)}
            print(f"{sol_file} error")
    finally:
        if err:
            err_file = ERROR_FOLDER / f"{file_name}.json"
            with err_file.open("w") as fp:
                json.dump(err, fp)
        else:
            print(f"{sol_file}")


def rename_runtime_file(folder):
    pass


if __name__ == '__main__':
    for hex_file in TARGET_FOLDER.iterdir():
        run(hex_file)
    # for re_run_file in RE_RUN:
    #     target = TARGET_FOLDER / f"{re_run_file}.json"
    #     target.unlink(missing_ok=True)
    #     run(TARGET_FOLDER / re_run_file)

