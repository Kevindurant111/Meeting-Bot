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
    key = 'story.txt'

    # Upload
    result = bucket.put_object_from_file("05f1483e-db4e-4504-a058-6fc87d3aafa6.mp4", "../upload/05f1483e-db4e-4504-a058-6fc87d3aafa6.mp4")
    print(result)
    # Download
    #bucket.get_object(key).read()

    # Delete
    # bucket.delete_object(key)

    # Traverse all objects in the bucket
    # for object_info in oss2.ObjectIterator(bucket):
    #     print(object_info.key)


def test_get_oss_url():

    endpoint = 'http://oss-cn-beijing.aliyuncs.com'
    auth = oss2.Auth(config['OSS']['id'], config['OSS']['secret'])
    bucket = oss2.Bucket(auth, endpoint, 'ap-ai01')

    object_name = '05f1483e-db4e-4504-a058-6fc87d3aafa6.mp4'

    # 指定HTTP查询参数。
    params = dict()
    # 设置单链接限速，单位为bit，例如限速100 KB/s。
    # params['x-oss-traffic-limit'] = str(100 * 1024 * 8)
    # 指定IP地址或者IP地址段。
    # params['x-oss-ac-source-ip'] = "127.0.0.1"
    # 指定子网掩码中1的个数。
    # params['x-oss-ac-subnet-mask'] = "32"
    # 指定VPC ID。
    # params['x-oss-ac-vpc-id'] = "vpc-t4nlw426y44rd3iq4xxxx"
    # 指定是否允许转发请求。
    # params['x-oss-ac-forward-allow'] = "true"

    # 生成下载文件的签名URL，有效时间为60秒。
    # 生成签名URL时，OSS默认会对Object完整路径中的正斜线（/）进行转义，从而导致生成的签名URL无法直接使用。
    # 设置slash_safe为True，OSS不会对Object完整路径中的正斜线（/）进行转义，此时生成的签名URL可以直接使用。
    url = bucket.sign_url('GET', object_name, 600, slash_safe=True, params=params)
    print('签名URL的地址为：', url)


#if __name__ == "__main__":


    # 创建转录任务
    # create_task_response = client.easyllm.speech_to_text.create(
    #     easyllm_id=config['API_KEYS']['easyllm_id'],
    #     audio_url="https://github.com/Kevindurant111/Meeting-Bot/releases/download/v1.0.0/demo.mp4",
    # )
    # print(create_task_response.task_id)
    # task_id = create_task_response.task_id

