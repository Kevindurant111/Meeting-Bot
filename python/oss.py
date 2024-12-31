import oss2
import configparser

def upload_to_oss(config_path, bucket_name, object_key, content):
    """
    上传内容到阿里云OSS存储。

    :param config_path: str 配置文件路径。
    :param bucket_name: str 存储桶名称。
    :param object_key: str 存储对象的键（路径和文件名）。
    :param content: str 要上传的内容。
    :return: bool 成功返回 True，失败返回 False。
    """
    try:
        # 读取配置
        config = configparser.ConfigParser()
        config.read(config_path)

        # 获取 OSS 配置信息
        endpoint = config['OSS']['endpoint']
        auth = oss2.Auth(config['OSS']['id'], config['OSS']['secret'])

        # 初始化存储桶
        bucket = oss2.Bucket(auth, endpoint, bucket_name)

        # 上传内容
        result = bucket.put_object(object_key, content)

        # 确认上传成功
        if result.status == 200:
            print(f"成功上传到 OSS：{bucket_name}/{object_key}")
            return True
        else:
            print(f"上传失败，状态码：{result.status}")
            return False

    except Exception as e:
        print(f"上传失败，错误信息：{e}")
        return False

def download_from_oss(config_path, bucket_name, object_key, download_path):
    """
    从阿里云OSS存储下载内容。

    :param config_path: str 配置文件路径。
    :param bucket_name: str 存储桶名称。
    :param object_key: str 存储对象的键（路径和文件名）。
    :param download_path: str 本地保存文件的路径。
    :return: bool 成功返回 True，失败返回 False。
    """
    try:
        # 读取配置
        config = configparser.ConfigParser()
        config.read(config_path)

        # 获取 OSS 配置信息
        endpoint = config['OSS']['endpoint']
        auth = oss2.Auth(config['OSS']['id'], config['OSS']['secret'])

        # 初始化存储桶
        bucket = oss2.Bucket(auth, endpoint, bucket_name)

        # 下载内容
        result = bucket.get_object(object_key)
        with open(download_path, 'wb') as file:
            file.write(result.read())

        print(f"成功从 OSS 下载到本地：{download_path}")
        return True

    except Exception as e:
        print(f"下载失败，错误信息：{e}")
        return False