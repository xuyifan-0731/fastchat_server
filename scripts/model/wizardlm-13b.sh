cd /workspace/xuyifan/xuyifan-old/serve/
model_name="WizardLM-13B-V1_2"
model_path="/workspace/checkpoint/WizardLM/WizardLM-13B-V1.2"
devices="6 6"
environment_name="vicuna"

/workspace/xuyifan/xuyifan-old/fastchat_server/scripts/worker-base.sh $model_name $model_path $environment_name "$devices"
