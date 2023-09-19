cd /workspace/xuyifan/xuyifan-old/serve
model_name="koala-13B"
model_path="/workspace/checkpoint/koala-13B-HF"
devices="7 7"
environment_name="vicuna"


/workspace/xuyifan/xuyifan-old/fastchat_server/scripts/worker-base.sh $model_name $model_path $environment_name $devices
