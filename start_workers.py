import subprocess
import time
import argparse, json

import socket

def find_next_available_port(start_port = 10020):
    port = start_port
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # 1 Second Timeout
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result != 0:  # Port is available
            return port
        port += 1
# def update(dst, src):
#     if isinstance(src, dict):
#         assert isinstance(dst, dict)
#         for k, v in src.items():
#             if k not in dst:
#                 dst[k] = v
#             else:
#                 dst[k] = update(dst[k], v)
#         return dst
#     elif isinstance(src, list):
#         assert isinstance(dst, list)
#         for i, v in enumerate(src):
#             dst[i] = update(dst[i], v)
#         return dst

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--devices", nargs="+", type=str, required=True)
    parser.add_argument("--controller_address", type=str, required=True)
    parser.add_argument("--host", type=str, required=True)
    parser.add_argument("--model-path", type=str, required=True)
    args = parser.parse_args()
    
    CONFIGS = {}
    CONFIGS["host"] = args.host
    CONFIGS["controller_address"] = args.controller_address
    workers = []
    ava_port = find_next_available_port()
    for device in args.devices:
        workers.append({"port":ava_port,"CUDA_VISIBLE_DEVICES":device})
        ava_port = find_next_available_port(ava_port + 1)
    CONFIGS["workers"] = workers
    
    logs_dir = "logs/%s/%s"%(CONFIGS["host"], time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))
    import os
    os.makedirs(logs_dir, exist_ok=True)
    print("logs_dir:", logs_dir)
    
    with open("%s/worker_starter.log"%(logs_dir), "a") as f:
        f.write("====== %s ======\n%s\n"%(time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()), json.dumps(CONFIGS, indent=4)))
        
    processes = []
    for idx, worker in enumerate(CONFIGS["workers"]):
        command = f"""CUDA_VISIBLE_DEVICES={worker["CUDA_VISIBLE_DEVICES"]} python worker.py \
            --host 0.0.0.0 \
            --port {worker["port"]} \
            --controller-address {CONFIGS["controller_address"]} \
            --worker-address http://{CONFIGS["host"]}:{worker["port"]} \
            --model-path {args.model_path} \
            --worker-id {idx} \
            --num-gpus {len(worker["CUDA_VISIBLE_DEVICES"].split(","))} --max-gpu-memory 64GiB\
            --logger_dir {logs_dir}"""
        with open("%s/worker_starter.log"%(logs_dir), "a") as f:
            f.write("====== %d ======\n%s\n"%(idx, command))
        print("=============\n%s\n============="%(command))
        process = subprocess.Popen(["bash", "-c", command], 
                #    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
        shell=False)
        processes.append(process)

    try:
        for process in processes:
            process: subprocess.Popen
            process.wait()
    except KeyboardInterrupt as e:
        print(">>> KeyboardInterrupt <<<")
        for process in processes:
            process: subprocess.Popen
            process.kill()
        exit()

# os.killpg(os.getpgid(process.pid), signal.SIGTERM)