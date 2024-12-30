# 使用SDK前需要安装python库 终端运行：pip install fastmodels-kit
from fastmodels import Client
import configparser
import time  # 用于实现等待

# 加载配置
config = configparser.ConfigParser()
config.read('../config.ini')

# 初始化客户端
client = Client(
    api_key=config['API_KEYS']['api_key'],
    project_id=config['API_KEYS']['project_id']
)

# # 创建转录任务
# create_task_response = client.easyllm.speech_to_text.create(
#     easyllm_id=config['API_KEYS']['easyllm_id'],
#     audio_url="https://github.com/Kevindurant111/Meeting-Bot/releases/download/v1.0.0/demo.mp3",
# )

# print(create_task_response.task_id)
# task_id = create_task_response.task_id

task_id = 11299831633
# 等待任务完成
MAX_RETRIES = 1000  # 最大重试次数
WAIT_INTERVAL = 5  # 每次等待的间隔时间（秒）
retries = 0

while retries < MAX_RETRIES:
    task = client.easyllm.speech_to_text.get(task_id)
    print(f"当前状态：{task.status}")
    if task.status != "waiting":
        break
    retries += 1
    time.sleep(WAIT_INTERVAL)

if task.status == "success":
    print("任务已完成！结果如下：")
    print(task.result)
elif retries >= MAX_RETRIES:
    print("任务超时，未完成。")
else:
    print(f"任务未成功，当前状态为：{task.status}")


# 初始化客户端
client = Client(
    api_key=config['API_KEYS']['meeting_minutes_api_key'],
    project_id=config['API_KEYS']['meeting_minutes_project_id']
)

# 调用接口
response = client.easyllm.meeting_minutes.create(
    easyllm_id=config['API_KEYS']['meeting_minutes_easyllm_id'],
    meeting_transcript=task.result
)

# 打印输出
print(response.choices[0].message.content)


