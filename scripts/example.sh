model_name="chatglm2-6b"
model_path="your checkpint path"
devices="0 0 0"
environment_name="base"


/workspace/xuyifan/xuyifan-old/fastchat_server/scripts/worker-base.sh $model_name $model_path $environment_name "$devices"
