#!/bin/bash

# Check if a minimum number of arguments were passed
if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <model_name> <model_path> [environment_name] [devices]"
  exit 1
fi

# Extract mandatory arguments
model_name=$1
model_path=$2

# Extract optional arguments or set default values
environment_name=${3:-"base"}
devices=${4:-"0"}

nvidia-smi
gpu_count=$(nvidia-smi -L | wc -l)
echo "Number of GPUs: $gpu_count"


# Start a new tmux session
tmux new-session -d -s $model_name

# Send various commands to the tmux session
tmux send-keys -t $model_name "export PYTHONPATH=/workspace/checkpoint/internlm/internlm-chat-7b-v1_1" C-m

tmux send-keys -t $model_name "controller_port=\"10010\"" C-m
tmux send-keys -t $model_name "source /workspace/xuyifan/miniconda3/etc/profile.d/conda.sh" C-m
tmux send-keys -t $model_name "conda activate $environment_name" C-m
tmux send-keys -t $model_name "cd /workspace/xuyifan/xuyifan-old/serve" C-m
tmux send-keys -t $model_name "hostname=\$(hostname -I | awk '{print \$1}')" C-m
tmux send-keys -t $model_name "echo \"Hostname: \$hostname\"" C-m
tmux send-keys -t $model_name "gpu_count=\$(nvidia-smi -L | wc -l)" C-m
tmux send-keys -t $model_name "echo \"Number of GPUs: \$gpu_count\"" C-m

# Conditionally send the Python command to start workers
if [ -z "$devices" ]; then
  tmux send-keys -t $model_name "python start_workers.py --host \$hostname --controller_address \"http://localhost:\$controller_port\" --model-path $model_path" C-m
else
  tmux send-keys -t $model_name "python start_workers.py --devices $devices --host \$hostname --controller_address \"http://localhost:\$controller_port\" --model-path $model_path" C-m
fi

# Attach to the tmux session
tmux attach-session -t $model_name
