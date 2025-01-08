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
   
2. **添加配置**：
   将服务Key添加到config.ini中。

3. **安装项目依赖**：
   ```bash
   pip3 install -r requirements.txt
   
4. **启动项目**：
项目基于 Flask 开发，可以通过以下命令启动：
   ```bash
   python3 ./python/web.py
   
Flask 应用将会在本地启动，默认监听在 http://127.0.0.1:5000/。

## 使用  

- 打开浏览器，访问 http://127.0.0.1:5000 。  
- 用户可以通过此页面上传会议视频文件（目前支持的文件类型为 .mp4、.wav 等常见视频格式）。  
- 上传文件后，机器人将开始处理视频，提取音频，进行语音识别，并生成会议纪要。  
- Meeting-Bot 还支持自动将生成的会议纪要通过电子邮件发送给指定的邮箱。该功能依赖于 Mailgun 服务。
