# Meeting-Bot

`Meeting-Bot` 是一个自动化机器人，能够根据录制的会议视频生成会议纪要。它使用语音识别技术和自然语言处理技术，将视频中的语音转化为文字，并生成会议纪要。

## 功能概述

- 从录制的会议视频中提取音频。
- 使用语音识别将音频转化为文本。
- 生成会议纪要，并发送到指定的邮箱。
- 支持文件上传功能，用户可以上传视频文件进行处理。

## 依赖

确保你的环境中安装了依赖，见 `requirements.txt`。

## 安装步骤

1. **克隆项目**：
   ```bash
   git clone https://github.com/yourusername/Meeting-Bot.git
   cd Meeting-Bot

2. **安装项目依赖**：
  ```bash
  pip install -r requirements.txt

3. **启动项目**：
项目基于 Flask 开发，可以通过以下命令启动：
  ```bash
  python3 ./python/web.py
Flask 应用将会在本地启动，默认监听在 http://127.0.0.1:5000/。
