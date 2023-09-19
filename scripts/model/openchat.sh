cd /workspace/xuyifan/xuyifan-old/serve
model_name="openchat"
model_path="/workspace/checkpoint/openchat/openchat_v3.2"
devices="0"
environment_name="fschat"


/workspace/xuyifan/xuyifan-old/fastchat_server/scripts/worker-base.sh $model_name $model_path $environment_name "$devices"
