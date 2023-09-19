cd /workspace/xuyifan/xuyifan-old/serve
model_name="internlm-chat-7b-v1_1"
model_path="/workspace/checkpoint/internlm/internlm-chat-7b-v1_1"
devices="4 4 4"
environment_name="intrenlm"

/workspace/xuyifan/xuyifan-old/fastchat_server/scripts/worker-base.sh $model_name $model_path $environment_name "$devices"