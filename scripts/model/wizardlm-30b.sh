cd /workspace/xuyifan/xuyifan-old/serve/
model_name="WizardLM-30B-V1_0-merged"
model_path="/workspace/checkpoint/WizardLM/WizardLM-30B-V1.0-merged"
devices="2 3"
environment_name="vicuna"

/workspace/xuyifan/xuyifan-old/fastchat_server/scripts/worker-base.sh $model_name $model_path $environment_name "$devices"
