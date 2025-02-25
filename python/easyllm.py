import json
import re
import time
from datetime import datetime
# from python.util import *
from python.util import *

class SpeechToTextMeetingProcessor:
    def __init__(self, config_path, log_file="../logs/transcription_log.txt"):
        # 加载配置
        #logger = None
        self.config = configparser.ConfigParser()
        self.config.read(config_path)

        self.MeetingNotesProcessor = MeetingNotesProcessor("../media/会议纪要-v1.0.1.docx")

        # 初始化转录客户端
        self.transcription_client = Client(
            api_key=self.config['API_KEYS']['api_key'],
            project_id=self.config['API_KEYS']['project_id']
        )

        # 初始化AI总结会议纪要客户端
        self.meeting_minutes_client = AIClient(self.config['API_KEYS']['meeting_minutes_api_key'], self.config['API_KEYS']['meeting_minutes_project_id'])

        # 初始化AI出题客户端
        self.meeting_question_client = AIClient(self.config['API_KEYS']['meeting_minutes_api_key'], self.config['API_KEYS']['meeting_minutes_project_id'])

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
            if task.status != "waiting" and task.status != "doing":
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
        response = self.meeting_minutes_client.create_and_run_agent(
            self.config["API_KEYS"]["meeting_minutes_initial"],
            transcript
        )
        return response

    def process_meeting_audio(self, audio_urls, generate_questions=False, meeting_content_path=None):
        """
        主流程：处理会议音频。
        """
        meeting_content = ""  # 用于存储所有拼接的转录内容

        if meeting_content_path is None:
            print("创建转录任务...")

            # 遍历 audio_urls 数组，逐个处理音频
            for idx, audio_url in enumerate(audio_urls):
                print(f"正在处理第 {idx + 1} 个音频: {audio_url}")

                # 创建转录任务
                task_id = self.create_transcription_task(audio_url)

                print("等待转录任务完成...")
                task = self.wait_for_transcription(task_id)

                if task is None or task.status != "success":
                    print(f"第 {idx + 1} 个音频任务未成功完成，跳过。")
                    continue

                print(f"第 {idx + 1} 个音频转录任务已完成。")

                # 拼接转录结果到 meeting_content
                meeting_content += task.result + "\n"

            if not meeting_content.strip():
                print("所有音频任务均未成功完成。")
                return None

            print("所有音频转录任务已完成，生成会议纪要...")

            # 保存会议内容到文本文件
            with open('meeting_content.txt', 'w', encoding='utf-8') as file:
                file.write(meeting_content)
            print("meeting_content 已保存到 meeting_content.txt")

            message = {"role": "user", "content": meeting_content}
            messages = [message]
        else:
            with open(meeting_content_path, 'r', encoding='utf-8') as file:
                meeting_content = file.read()  # 读取文件的每一行
            print(meeting_content)
            message = {"role": "user", "content": meeting_content}
            messages = [message]    
        meeting_minutes = self.meeting_minutes_client.create_and_run_agent(
            self.config["API_KEYS"]["meeting_minutes_initial"],
            messages
        )
        #meeting_minutes = self.create_meeting_minutes(task.result) # 停用直接使用固定模型总结会议纪要的方式，改为使用Agent定制化
        logger.info("minutes: %s", meeting_minutes)
        # 找到第一个 "{" 和最后一个 "}"
        start = meeting_minutes.find("{")  # 第一个 "{" 的索引
        end = meeting_minutes.rfind("}")   # 最后一个 "}" 的索引

        # 提取第一个 "{" 和最后一个 "}" 之间的内容
        if start != -1 and end != -1:  # 确保 "{" 和 "}" 存在
            meeting_minutes = meeting_minutes[start:end + 1]
        else:
            meeting_minutes = ""  # 如果没有找到 "{" 或 "}"，返回空字符串
        meeting_minutes_dict = json.loads(meeting_minutes)
        print(";".join(map(str, meeting_minutes_dict["行动计划"])))
        self.MeetingNotesProcessor._record_content("会议主题", meeting_minutes_dict["会议主题"])
        self.MeetingNotesProcessor._record_content("会议主持", meeting_minutes_dict["会议主持人"])
        self.MeetingNotesProcessor._record_content("会议要点", ",".join(map(str, meeting_minutes_dict["会议要点"])))
        self.MeetingNotesProcessor._record_content("会议结论", ",".join(map(str, meeting_minutes_dict["会议结论"])))
        self.MeetingNotesProcessor._record_content("参会人员", ",".join(map(str, meeting_minutes_dict["参会人员"])))
        self.parse_and_add_action_items(";".join(map(str, meeting_minutes_dict["行动计划"])))
        self.MeetingNotesProcessor.save()

        # If questions need to be generated, trigger that process
        if generate_questions:
            print("Generating questions from the meeting minutes...")

            questions = self.generate_questions_from_meeting(meeting_minutes)
            # if meeting_content_path is None:
            #     questions = self.generate_questions_from_meeting(task.result)
            # else:
            #     questions = self.generate_questions_from_meeting(meeting_content)

            # 保存 questions 到文本文件
            with open('questions.txt', 'w', encoding='utf-8') as file:
                file.write(questions + '\n')
            print("Questions have been saved to questions.txt")

        return meeting_minutes

    def generate_questions_from_meeting(self, meeting_content):
        """
        Generate relevant questions based on the meeting content.
        :return: String containing generated questions
        """
        message = {"role": "user", "content": '这一段是会议内容: ' + meeting_content}
        messages = [message]
        meeting_questions = self.meeting_question_client.create_and_run_agent(
            self.config["API_KEYS"]["meeting_question_initial"],
            messages
        )
        return meeting_questions
    
    def parse_and_add_action_items(self, text):
        """
        解析事项文本并将解析结果通过 add_action_item 函数添加到文档表格中。

        :param text: 包含事项信息的文本
        """
        # 定义正则表达式来匹配每一行的内容，以中文逗号为分隔符
        #attern = r"\d+：([^，]+)，负责人：([^，]+)，完成时间：([^;]+)"
        #pattern = r"([^，]+)，负责人：([^，]+)，完成时间：([^;]+)"
        pattern = r"(?:^|;)\s*([^，]+)，负责人：([^，]+)，完成时间：([^;]+)"
        
        # 使用正则表达式搜索匹配
        matches = re.findall(pattern, text)
        
        # 遍历匹配的事项信息，调用 add_action_item 插入到表格中
        for idx, match in enumerate(matches, start=1):
            item = match[0].strip()  # 事项内容
            responsible = match[1].strip()  # 负责人
            deadline = match[2].strip()  # 完成时间
            
            # 自动生成 serial_number
            serial_number = idx
            
            # 调用 add_action_item 函数将数据插入到文档表格中
            self.MeetingNotesProcessor.add_action_item(serial_number, item, responsible, deadline)

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

    def get_last_logged_task_status(self, max_retries=1000, wait_interval=5):
        """
        从日志文件中读取最后一条记录的 task_id，并实时查询其任务状态。
        """
        last_task_id = self.get_last_logged_task_id()
        if not last_task_id:
            print("日志中没有找到任何任务记录。")
            return None

        print(f"开始查询最后一个任务 ID: {last_task_id} 的实时状态...")
        task = self.poll_task_by_id(last_task_id, max_retries, wait_interval)
        
        if task:
            print(f"任务 {last_task_id} 的最终状态为: {task.status}")
            return task.status
        else:
            print(f"任务 {last_task_id} 查询失败或超时。")
            return None

# 使用示例
if __name__ == "__main__":
    processor = SpeechToTextMeetingProcessor(config_path="../config.ini")
    audio_url = "http://ap-ai01.oss-cn-beijing.aliyuncs.com/TcbMeeting.mp4?OSSAccessKeyId=LTAI5tA7t6xe64Y8PdgPmwtg&Expires=5340365400&Signature=19NZB41dYqDVlhw4dFvou%2FZUFYA%3D"
    result = processor.process_meeting_audio(audio_url, True, './meeting_content.txt')


