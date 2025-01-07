import configparser
import time

import oss2
from fastmodels import Client

# 等待任务完成
MAX_RETRIES = 50  # 最大重试次数
WAIT_INTERVAL = 5  # 每次等待的间隔时间（秒）

# 加载配置
config = configparser.ConfigParser()
config.read('../config.ini')

# 初始化客户端
client = Client(
    api_key=config['API_KEYS']['api_key'],
    project_id=config['API_KEYS']['project_id']
)

def test_model():
    task_id = 11299831633
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

def test_oss():

    endpoint = 'http://oss-cn-beijing.aliyuncs.com'
    auth = oss2.Auth(config['OSS']['id'], config['OSS']['secret'])
    bucket = oss2.Bucket(auth, endpoint, 'ap-ai01')

    # The object key in the bucket is story.txt
    key = 'story1.txt'

    # Upload
    bucket.put_object(key, 'Ali Baba is a happy youth.')

    # Download
    #bucket.get_object(key).read()

    # Delete
    # bucket.delete_object(key)

    # Traverse all objects in the bucket
    # for object_info in oss2.ObjectIterator(bucket):
    #     print(object_info.key)

#if __name__ == "__main__":


    # 创建转录任务
    # create_task_response = client.easyllm.speech_to_text.create(
    #     easyllm_id=config['API_KEYS']['easyllm_id'],
    #     audio_url="https://github.com/Kevindurant111/Meeting-Bot/releases/download/v1.0.0/demo.mp4",
    # )
    # print(create_task_response.task_id)
    # task_id = create_task_response.task_id

