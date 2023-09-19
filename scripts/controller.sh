source /workspace/xuyifan/miniconda3/etc/profile.d/conda.sh
conda activate base
cd /workspace/xuyifan/xuyifan-old/serve

hostname=$(hostname -I | awk '{print $1}')
echo "Hostname: $hostname"
gpu_count=$(nvidia-smi -L | wc -l)
echo "Number of GPUs: $gpu_count"

apt-get update
apt-get install -y tmux 
apt-get install -y jq 
tmux new-session -d -s controller
tmux send-keys -t controller "source /workspace/xuyifan/miniconda3/etc/profile.d/conda.sh" C-m
tmux send-keys -t controller "conda activate base" C-m
tmux send-keys -t controller "cd /workspace/xuyifan/xuyifan-old/serve" C-m
tmux send-keys -t controller "controller_port="10010"" C-m
tmux send-keys -t controller 'python controller.py --port $controller_port' C-m

sleep 3
echo "Controller started" >> /workspace/xuyifan/xuyifan-old/serve/test-log.txt
