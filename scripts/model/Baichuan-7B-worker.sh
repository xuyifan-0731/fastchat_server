model_name="Baichuan-7B"
model_path="/workspace/checkpoint/baichuan-inc/Baichuan-7B"
devices="4 4 4 5 5 5 6 6 6 7 7 7"
environment_name="vicuna"

/workspace/xuyifan/xuyifan-old/fastchat_server/scripts/worker-base.sh $model_name $model_path $environment_name "$devices"


