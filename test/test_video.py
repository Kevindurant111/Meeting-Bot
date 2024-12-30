import subprocess
import json

def has_subtitle_stream(file_path):
    try:
        # 使用 ffprobe 获取视频文件信息
        command = [
            'ffprobe', 
            '-v', 'error', 
            '-select_streams', 's',  # 选择字幕流
            '-show_entries', 'stream=index', 
            '-of', 'json', 
            file_path
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # 解析 JSON 结果
        streams = json.loads(result.stdout).get('streams', [])
        
        # 检查是否有字幕流
        return len(streams) > 0
    except Exception as e:
        print(f"Error checking subtitle stream: {e}")
        return False

# 示例用法
file_path = '../meeting_01.mp4'
if has_subtitle_stream(file_path):
    print("视频包含字幕流")
else:
    print("视频不包含字幕流")
