cd /workspace/xuyifan/xuyifan-old/serve
model_name="vicuna-13b-v1_5"
model_path="/workspace/checkpoint/lmsys/vicuna-13b-v1.5"
devices="6 6"

environment_name="vicuna"

/workspace/xuyifan/xuyifan-old/fastchat_server/scripts/worker-base.sh $model_name $model_path $environment_name "$devices"

