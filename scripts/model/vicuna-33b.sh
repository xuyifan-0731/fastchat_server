model_name="vicuna-33b-v1_3"
model_path="/workspace/checkpoint/lmsys/vicuna-33b-v1.3"

devices="0 1"
environment_name="vicuna"

/workspace/xuyifan/xuyifan-old/fastchat_server/scripts/worker-base.sh $model_name $model_path $environment_name "$devices"