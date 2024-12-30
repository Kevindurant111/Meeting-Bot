# 使用SDK前需要安装python库  终端运行：pip install fastmodels-kit
from fastmodels import Client
import configparser

config = configparser.ConfigParser()
config.read('../config.ini')

# 初始化客户端
client = Client(
    api_key= config['API_KEYS']['api_key'],
    project_id= config['API_KEYS']['project_id']
)
# # 创建转录任务
# create_task_response = client.easyllm.speech_to_text.create(
#     easyllm_id=config['API_KEYS']['easyllm_id'],
#     audio_url="https://drive.google.com/file/d/18uvPASlQea85PGlFZURZIUHIC4FtHsXE/view?usp=sharing",
# )

# print(create_task_response)
# print(create_task_response.task_id)
# task_id = create_task_response.task_id

task_id = 11299279156
task = client.easyllm.speech_to_text.get(task_id)
print(task.status)
print(task.result)