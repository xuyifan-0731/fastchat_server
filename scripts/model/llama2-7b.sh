cd /workspace/xuyifan/xuyifan-old/serve/
model_name="llama2-chat-7b"
model_path="/workspace/checkpoint/meta/Llama-2-7b-chat-hf"

devices="2 2 2"
environment_name="base"

/workspace/xuyifan/xuyifan-old/fastchat_server/scripts/worker-base.sh $model_name $model_path $environment_name "$devices"