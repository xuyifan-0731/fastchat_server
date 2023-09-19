cd /workspace/xuyifan/xuyifan-old/serve
model_name="Baichuan-13B-Chat"
model_path="/workspace/checkpoint/baichuan-inc/Baichuan-13B-Chat"
devices="0 0"
environment_name="vicuna"

/workspace/xuyifan/xuyifan-old/fastchat_server/scripts/worker-base.sh $model_name $model_path $environment_name "$devices"