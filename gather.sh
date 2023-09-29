bash /workspace/xuyifan/xuyifan-old/serve/scripts/controller.sh
bash /workspace/xuyifan/xuyifan-old/serve/scripts/wizardlm-13b.sh
bash /workspace/xuyifan/xuyifan-old/serve/check.sh

source /workspace/xuyifan/miniconda3/etc/profile.d/conda.sh
conda activate base
cd /workspace/xuyifan/xuyifan-old/STEPS_benchmark
bash test-sh/wizard-13.sh