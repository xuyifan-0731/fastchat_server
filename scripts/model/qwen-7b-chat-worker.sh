model_name="Qwen-7B-chat"
model_path="/workspace/checkpoint/Qwen/Qwen-7B-Chat"
devices="5 5 5"
environment_name="base"

/workspace/xuyifan/xuyifan-old/fastchat_server/scripts/worker-base.sh $model_name $model_path $environment_name "$devices"
