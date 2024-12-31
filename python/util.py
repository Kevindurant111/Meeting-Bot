import configparser
import requests

# log_config.py
import logging
import os

# 配置日志文件路径
LOG_DIR = '../logs'  # 日志目录
LOG_FILE = 'app.log'  # 日志文件名
LOG_PATH = os.path.join(LOG_DIR, LOG_FILE)

# 创建日志目录（如果不存在）
os.makedirs(LOG_DIR, exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,  # 设置日志级别
    format='%(asctime)s - %(levelname)s - %(message)s',  # 日志格式
    handlers=[
        logging.FileHandler(LOG_PATH, encoding='utf-8'),
        logging.StreamHandler()  # 也可以输出到控制台

    ]
)

logger = logging.getLogger(__name__)  # 创建一个日志记录器


class Util:
    _instance = None

    def __init__(self):
        self.mail_domain = None
        self.mail_url = None
        self.mail_api_key = None
        self.oss_api_secret = None
        self.oss_api_key = None
        self.esm_project_id = None
        self.esm_id = None
        self.esm_api_key = None

    def __new__(self, *args, **kwargs):
        if not self._instance:
            self._instance = super(Util, self).__new__(self)
            self._instance.init()
        return self._instance

    def init(self):
        config_dict = configparser.ConfigParser()
        self.esm_api_key = config_dict["API_KEYS"]["api_key"]
        self.esm_id = config_dict["API_KEYS"]["easyllm_id"]
        self.esm_project_id = config_dict["API_KEYS"]["project_id"]
        self.oss_api_key = config_dict["OSS"]["id"]
        self.oss_api_secret = config_dict["OSS"]["secret"]
        self.mail_api_key = config_dict["MAILGUN"]["api_key"]
        self.mail_url = config_dict["MAILGUN"]["url"]
        self.mail_domain = config_dict["MAILGUN"]["domain"]
        logger.info("Finished config init")

    def send_email(self, to_addresses, subject, context, file_path):
        if file_path:
            response = requests.post(
                self.mail_url,
                auth=(self.mail_domain, self.mail_api_key),
                files=[("attachment", open(file_path, "rb"))],  # 添加附件
                data={"from": "operation@antpool.com",
                      "to": to_addresses,
                      "subject": subject,
                      "text": context})
        else:
            response = requests.post(
                self.mail_url,
                auth=(self.mail_domain, self.mail_api_key),
                data={"from": "operation@antpool.com",
                      "to": to_addresses,
                      "subject": subject,
                      "text": context})
        logger.info("Call mailgun %s", response.json())


