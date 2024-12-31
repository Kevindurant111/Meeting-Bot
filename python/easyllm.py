import configparser
import time
from datetime import datetime

from fastmodels import Client
from util import logger


class SpeechToTextMeetingProcessor:
    def __init__(self, config_path):
        # 加载配置
        self.config = configparser.ConfigParser()
        self.config.read(config_path)

        # 初始化转录客户端
        self.transcription_client = Client(
            api_key=self.config['API_KEYS']['api_key'],
            project_id=self.config['API_KEYS']['project_id']
        )

        # 初始化会议纪要客户端
        self.meeting_minutes_client = Client(
            api_key=self.config['API_KEYS']['meeting_minutes_api_key'],
            project_id=self.config['API_KEYS']['meeting_minutes_project_id']
        )

        # 设置日志记录
        # logging.basicConfig(
        #     filename=log_file,
        #     level=logging.INFO,
        #     format="%(asctime)s - %(message)s"
        # )
        # logger = logging.getLogger()
        # self.log_file = log_file

    def create_transcription_task(self, audio_url):
        """
        创建转录任务。
        """
        response = self.transcription_client.easyllm.speech_to_text.create(
            easyllm_id=self.config['API_KEYS']['easyllm_id'],
            audio_url=audio_url
        )
        task_id = response.task_id
        logger.info(f"Task created. Task ID: {task_id}, Start Time: {datetime.now()}")
        return task_id

    def wait_for_transcription(self, task_id, max_retries=1000, wait_interval=5):
        """
        等待转录任务完成。
        """
        retries = 0
        start_time = datetime.now()

        while retries < max_retries:
            task = self.transcription_client.easyllm.speech_to_text.get(task_id)
            print(f"当前状态：{task.status}")
            if task.status != "waiting":
                end_time = datetime.now()
                logger.info(
                    f"Task completed. Task ID: {task_id}, Start Time: {start_time}, "
                    f"End Time: {end_time}, Status: {task.status}"
                )
                if task.status == "success":
                    logger.info(f"Transcription Result: {task.result}")
                return task
            retries += 1
            time.sleep(wait_interval)

        # 超时未完成
        end_time = datetime.now()
        logger.info(
            f"Task timeout. Task ID: {task_id}, Start Time: {start_time}, "
            f"End Time: {end_time}, Status: timeout"
        )
        return None

    def create_meeting_minutes(self, transcript):
        """
        调用会议纪要生成接口。
        """
        response = self.meeting_minutes_client.easyllm.meeting_minutes.create(
            easyllm_id=self.config['API_KEYS']['meeting_minutes_easyllm_id'],
            meeting_transcript=transcript
        )
        return response.choices[0].message.content

    def process_meeting_audio(self, audio_url):
        """
        主流程：处理会议音频。
        """
        print("创建转录任务...")
        task_id = self.create_transcription_task(audio_url)

        print("等待转录任务完成...")
        task = self.wait_for_transcription(task_id)

        if task is None or task.status != "success":
            print("任务未成功完成。")
            return None

        print("转录任务已完成，生成会议纪要...")
        meeting_minutes = self.create_meeting_minutes(task.result)
        return meeting_minutes

    def poll_task_by_id(self, task_id, max_retries=1000, wait_interval=5):
        """
        根据 task_id 轮询任务状态。
        """
        print(f"开始轮询任务 {task_id} 的状态...")
        return self.wait_for_transcription(task_id, max_retries, wait_interval)

    def get_last_logged_task_id(self):
        """
        从日志文件中读取最后一条记录的 task_id。
        """
        with open(self.log_file, "r") as file:
            lines = file.readlines()
        for line in reversed(lines):
            if "Task ID:" in line:
                task_id = line.split("Task ID:")[1].split(",")[0].strip()
                return task_id
        return None

    def get_last_logged_task_status(self):
        """
        从日志文件中读取最后一条记录的任务状态。
        """
        with open(self.log_file, "r") as file:
            lines = file.readlines()
        for line in reversed(lines):
            if "Status:" in line:
                status = line.split("Status:")[1].strip()
                return status
        return None


# 使用示例
if __name__ == "__main__":
    processor = SpeechToTextMeetingProcessor(config_path="../config.ini")

    # 处理新的音频文件
    # audio_url = "https://github.com/Kevindurant111/Meeting-Bot/releases/download/v1.0.0/demo.mp3"
    audio_url = "http://ap-ai01.oss-cn-beijing.aliyuncs.com/demo.wav?OSSAccessKeyId=LTAI5tA7t6xe64Y8PdgPmwtg&Expires=1735634405&Signature=aGaYQ0kaNOy37%2BmJM0tYgMLKYH4%3D"
    result = processor.process_meeting_audio(audio_url)

    if result:
        print("会议纪要生成成功：")
        print(result)
    else:
        print("会议纪要生成失败。")

    # 通过 task_id 查询任务状态
    last_task_id = processor.get_last_logged_task_id()
    if last_task_id:
        print(f"最后一个记录的任务 ID: {last_task_id}")
        task_status = processor.poll_task_by_id(last_task_id)
        print(f"最后一个任务的状态: {task_status}")
    else:
        print("日志中没有找到任何任务记录。")
