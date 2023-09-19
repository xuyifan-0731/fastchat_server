# fastchat_server

1. 创建对应模型能够运行的环境
2. bash scripts/controller.sh
3. 修改 scripts中的对应模型配置文件：
    3.1 model_name,model_path按照实际情况填写
    3.2 指定devices：一个字符串，每个数字对应在第x张卡上部署一个模型
    3.3 environment_name：环境名称
4. bash scripts/model.sh