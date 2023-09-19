#!/bin/bash
model_name="WizardLM-13B-V1.2"
while true; do
    response=$(curl -s -H "Content-Type: application/json" -X POST localhost:10010/list_models)
    models=$(echo $response | jq -r '.models[]')
    for model in $models; do
        echo "Checking model $model_name" >> /workspace/xuyifan/xuyifan-old/serve/test-log.txt
        if [[ $model == $model_name ]]; then
            echo "Model $model_name found. Executing the next command..." >> /workspace/xuyifan/xuyifan-old/serve/test-log.txt
            break 2
        fi
    done
    sleep 3
done

sleep 10