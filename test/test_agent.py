import time
import threading
from fastmodels import Client
from pytwitter import Api
import configparser
from web3 import Web3

class AIClient:
    def __init__(self, config):
        """
        初始化 AI 客户端，连接到 fastmodels API。
        
        :param config: 配置文件中的参数。
        """
        self.client = Client(api_key=config['API_KEYS']['agent_api_key'], project_id=config['API_KEYS']['agent_project_id'])
        self.agent_id_initial = config['API_KEYS']['agent_id_initial']  # 初始代理ID
        self.thread_id = None

    def create_and_run_agent(self, messages):
        """
        创建并运行代理，发送消息并获取回复。

        :param agent_id: 代理 ID。
        :param messages: 用户消息列表。
        :param thread_id: 线程 ID。
        :return: 代理响应内容。
        """
        if self.thread_id is None:
            response = self.client.agent.threads.create_and_run(
                agent_id=self.agent_id_initial,
                messages=messages
            )
            self.thread_id = response.thread_id
        else:
            response = self.client.agent.threads.create_and_run(
                agent_id=self.agent_id_initial,
                thread_id=self.thread_id,
                messages=messages
            )

        return response.content[0].text.value

def main():
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read('../config.ini')
    messages=[
        {"role": "user", "content": """
    # 会议纪要：
    这是一场关于AI大赛产品设计及TCB编写的项目会议。会议主要讨论了产品设计、项目进度、TCB构成及待办事项安排。参会者详细讨论了如何进行产品设计和编写TCB，以及具体的后续任务分工。

    ## 要点1：产品设计
    当前设计了一个网页，可以上传会议的音频或视频文件，系统自动解析并转录成文字，由AI生成会议纪要，并填充到模板中，通过邮件发送会议纪要附件。

    ## 要点2：关键问题（KP）
    会议纪要生成过程复杂，耗费人员精力，需IT化、自动化以响应降本增效。

    ## 要点3：项目进度
    - 目前代码框架及工具已完成，还需进行前后端对接及业务逻辑调用，最终将会议纪要填充到Word模板中。
    - 发邮件的代码已经完成，需进行代码重构以简化流程。

    ## 要点4：TCB编写
    - TCB文档用于指导一次性任务，形式为PPT，需展示背景、关键问题（KP）、目标（KO）及策略（KT），并包括项目预算。
    - 背景：会议纪要生成复杂，耗费人力。
    - 目标（KO）：释放人力，实现降本增效。
    - 任务（Task）：自动生成会议纪要。

    ## 要点5：任务分配
    - 重构代码：张骞
    - 填写Word模板：翟乾浩
    - 完成TCB编写：徐雅楠

    # 会议结论：
    本次会议围绕AI大赛的产品设计、项目进度、TCB构成等方面进行了深入讨论。会议指出了会议纪要生成过程的复杂性，并强调需要通过IT化和自动化来实现降本增效。同时，对项目进度进行了汇报，明确了剩余任务及责任人。会议还详细讨论了TCB的构成及编写要求，最后分配了具体任务和时间要求。

    # 待办事项:
    1. 张骞负责重构代码;
    2. 翟乾浩负责完善Word模板填写;
    3. 徐雅楠完成TCB的编写，截止日期为1月6日;
    告诉我会议主题。
    """}
    ]
    agent = AIClient(config)
    print(agent.create_and_run_agent(messages))

if __name__ == "__main__":
    main()
   