cd /workspace/xuyifan/xuyifan-old/serve/
model_name="guanaco-33b-merged"
model_path="/workspace/checkpoint/timdettmers/guanaco-33b-merged"
devices="4 5"
environment_name="vicuna"

/workspace/xuyifan/xuyifan-old/fastchat_server/scripts/worker-base.sh $model_name $model_path $environment_name "$devices"
