cd /workspace/xuyifan/xuyifan-old/serve
model_name="oasst-sft-4-pythia-12b"
model_path="/workspace/checkpoint/OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5"
devices="0 0"
environment_name="base"

/workspace/xuyifan/xuyifan-old/fastchat_server/scripts/worker-base.sh $model_name $model_path $environment_name "$devices"