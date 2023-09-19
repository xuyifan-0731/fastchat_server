model_name="chatglm2-12b"
model_path="/workspace/checkpoint/chatglm/chatglm2-12b"
devices="1 1"
environment_name="base"


/workspace/xuyifan/xuyifan-old/fastchat_server/scripts/worker-base.sh $model_name $model_path $environment_name "$devices"
