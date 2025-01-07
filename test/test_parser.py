import re

class MeetingSummaryParser:
    def __init__(self, meeting_text):
        """
        初始化方法，解析会议纪要文本并提取各项信息
        
        :param meeting_text: 包含会议内容的文本。
        """
        self.meeting_text = meeting_text
        self.summary = ""
        self.key_points = []
        self.tasks = []
        self.conclusion = ""
        self.extract_meeting_info()

    def extract_meeting_info(self):
        """
        提取会议纪要中的各项信息，包括会议总结、要点、任务和会议结论。
        """
        # 提取会议纪要最开始的部分（假设为 # 会议纪要: 后面的第一段）
        summary_match = re.search(r'# 会议纪要：\s*(.*?)\n\n', self.meeting_text, re.DOTALL)
        if summary_match:
            self.summary = summary_match.group(1).strip()

        # 提取要点部分
        key_points_match = re.findall(r'## 要点\d：([^\n]+)\n([^#]+)', self.meeting_text)
        for point in key_points_match:
            self.key_points.append({"title": point[0].strip(), "content": point[1].strip()})

        # 提取待办事项
        tasks_match = re.findall(r'^\d+\.\s*(.*?)\s*;?$', self.meeting_text, re.MULTILINE)
        for task in tasks_match:
            self.tasks.append(task.strip())

        # 提取会议结论部分
        conclusion_match = re.search(r'# 会议结论：\s*(.*?)\n\n', self.meeting_text, re.DOTALL)
        if conclusion_match:
            self.conclusion = conclusion_match.group(1).strip()

    def get_summary(self):
        return self.summary

    def get_key_points(self):
        return self.key_points

    def get_tasks(self):
        return self.tasks

    def get_conclusion(self):
        return self.conclusion

# 示例使用
if __name__ == "__main__":
    meeting_text = """
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
    """

    parser = MeetingSummaryParser(meeting_text)

    print("会议纪要：")
    print(parser.get_summary())
    print("\n要点：")
    for idx, point in enumerate(parser.get_key_points(), 1):  # 使用 enumerate 来获取索引，从 1 开始
        print(f"要点{idx}：\n{point['content']}\n")
    print("\n待办事项：")
    for task in parser.get_tasks():
        print(f"- {task}")
    print("\n会议结论：")
    print(parser.get_conclusion())
