import configparser
import time

import oss2
from fastmodels import Client

from python.easyllm import SpeechToTextMeetingProcessor

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


#def test_model():
    # task_id = 11299831633
    # retries = 0
    # while retries < MAX_RETRIES:
    #     task = client.easyllm.speech_to_text.get(task_id)
    #     print(f"当前状态：{task.status}")
    #     if task.status != "waiting":
    #         break
    #     retries += 1
    #     time.sleep(WAIT_INTERVAL)
    # if task.status == "success":
    #     print("任务已完成！结果如下：")
    #     print(task.result)
    # elif retries >= MAX_RETRIES:
    #     print("任务超时，未完成。")
    # else:
    #     print(f"任务未成功，当前状态为：{task.status}")


def test_oss():
    endpoint = 'http://oss-cn-beijing.aliyuncs.com'
    auth = oss2.Auth(config['OSS']['id'], config['OSS']['secret'])
    bucket = oss2.Bucket(auth, endpoint, 'ap-ai01')

    for i in range(10):
        filename = f"20250222110619-36期主管培训-视频-1_{i + 1}.mp3"
        # 上传内容
        result = bucket.put_object_from_file(filename, "..\\upload\\" + filename)
        time.sleep(5)


    # Download
    # bucket.get_object(key).read()

    # Delete
    # bucket.delete_object(key)

    # Traverse all objects in the bucket
    # for object_info in oss2.ObjectIterator(bucket):
    #     print(object_info.key)


# if __name__ == "__main__":


# 创建转录任务
# create_task_response = client.easyllm.speech_to_text.create(
#     easyllm_id=config['API_KEYS']['easyllm_id'],
#     audio_url="https://github.com/Kevindurant111/Meeting-Bot/releases/download/v1.0.0/demo.mp4",
# )
# print(create_task_response.task_id)
# task_id = create_task_response.task_id

def test_process():
    # AI解析视频文件
    processor = SpeechToTextMeetingProcessor(config_path="../config.ini")
    # 处理新的音频文件
    processor.process_meeting_audio(
        "https://ap-ai01.oss-cn-beijing.aliyuncs.com/20250222110619-36%E6%9C%9F%E4%B8%BB%E7%AE%A1%E5%9F%B9%E8%AE%AD-%E8%A7%86%E9%A2%91-1.mp3?Expires=1740419176&OSSAccessKeyId=TMP.3KkRZgLMDyBctAz6a4UF7H47LDBdFTFS5wwmEQcZuuAXQm17RJaTrcjZPJhJfxbxS7286b8D8xPiefZkCz8gUNYYVypPh8&Signature=2omYPxOXvdi6YLKNqCujX%2Fn7nXk%3D")
    # util = Util()
    # util.init()
    # util.send_email("nilszhang001@gmail.com", "会议纪要", "这是根据您上传视频生成的会议纪要，请查收。", "./result.docx")
