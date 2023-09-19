cd /workspace/xuyifan/xuyifan-old/serve
model_name="dolly-v2-12b"
model_path="/workspace/checkpoint/dolly-v2-12b"
devices="4 4"
environment_name="base"

/workspace/xuyifan/xuyifan-old/fastchat_server/scripts/worker-base.sh $model_name $model_path $environment_name "$devices"