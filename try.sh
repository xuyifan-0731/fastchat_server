CUDA_VISIBLE_DEVICES=6,7 python worker.py \
    --host 0.0.0.0             \
    --port 9993             \
    --controller-address http://192.18.128.201:40000             \
    --worker-address http://192.18.130.169:9993             \
    --model-path /workspace/yuhao/checkpoints/huggingface/timdettmers/guanaco-65b-merged             \
    --worker-id 3             \
    --num-gpus 2 \
    --max-gpu-memory 60GiB            \
    --logger_dir logs/test

CUDA_VISIBLE_DEVICES=1 python worker.py \
    --host 0.0.0.0             \
    --port 9123             \
    --controller-address http://192.18.128.201:40000             \
    --worker-address http://192.18.140.88:9123             \
    --model-path /workspace/yuhao/checkpoints/huggingface/openchat/openchat_8192           \
    --worker-id 3             \
    --num-gpus 1 \
    --max-gpu-memory 60GiB            \
    --logger_dir logs/test