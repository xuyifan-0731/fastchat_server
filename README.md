# fastchat_server

1. 创建对应模型能够运行的环境
2. bash scripts/controller.sh
3. 修改 scripts中的对应模型配置文件：
    3.1 model_name,model_path按照实际情况填写。大多数model_name已经添加到scripts/model文件夹中，复制即可
    3.2 指定devices：一个字符串，每个数字对应在第x张卡上部署一个模型。例如“0 0 0”表示在0号卡布置三个模型。一般情况下，7b大小模型可以布置三个，13b大小模型可以布置2个。
    3.3 environment_name：环境名称。注意可能有些模型的运行环境互相冲突
4. bash scripts/[你的模型文件].sh 可以参考bash scripts/example.sh