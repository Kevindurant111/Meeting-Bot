from flask import Flask, request, render_template_string, redirect, url_for
import uuid  # 用于生成唯一的taskid

from easyllm import SpeechToTextMeetingProcessor
from util import *
import oss

app = Flask(__name__)

# 设置文件上传的保存路径
UPLOAD_FOLDER = '../upload'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # 确保上传文件夹存在
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 支持的文件格式
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'flv', 'mp4', 'wma'}

# 全局字典存储上传信息
uploaded_files = {}

# 检查文件是否为允许的格式
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 首页：显示文件上传表单
@app.route('/')
def upload_form():
    success = request.args.get('success', 'false') == 'true'  # 检查是否有成功提示
    return render_template_string('''
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>会议纪要生成工具</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .required:after {
                content: " *";
                color: red;
            }
        </style>
        <script>
            function validateFile() {
                const allowedExtensions = ['wav', 'mp3', 'm4a', 'flv', 'mp4', 'wma'];
                const fileInput = document.getElementById('file');
                const filePath = fileInput.value;
                const fileExtension = filePath.split('.').pop().toLowerCase();

                if (!allowedExtensions.includes(fileExtension)) {
                    const modal = new bootstrap.Modal(document.getElementById('errorModal'));
                    modal.show();
                    fileInput.value = '';
                    return false;
                }
                return true;
            }

            function clearFileInput() {
                document.getElementById('file').value = '';
            }

            function clearUrlParams() {
                const url = new URL(window.location.href);
                url.searchParams.delete('success');
                window.history.replaceState({}, document.title, url);
            }
        </script>
    </head>
    <body>
        <div class="container mt-5">
            <div class="card shadow-sm">
                <div class="card-header bg-primary text-white">
                    <h3 class="card-title text-center">会议纪要生成工具</h3>
                </div>
                <div class="card-body">
                    <form method="post" action="/upload" enctype="multipart/form-data" onsubmit="return validateFile()">
                        <div class="mb-3">
                            <label for="taskid" class="form-label required">任务ID：</label>
                            <input class="form-control" type="text" id="taskid" name="taskid" value="{{ taskid }}" readonly>
                        </div>
                        <div class="mb-3">
                            <label for="file" class="form-label required">选择文件：</label>
                            <input class="form-control" type="file" id="file" name="file" required>
                            <div class="form-text text-muted mt-2">
                                支持的文件格式：<strong>wav, mp3, m4a, flv, mp4, wma</strong>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label for="email" class="form-label required">邮箱地址：</label>
                            <input class="form-control" type="email" id="email" name="email" required>
                            <div class="form-text text-muted mt-2">
                                我们会将会议纪要文件发送到您的邮箱。
                            </div>
                        </div>
                        <div class="mb-3">
                            <label for="participants" class="form-label">参会人：</label>
                            <input class="form-control" type="text" id="participants" name="participants" placeholder="多个参会人用逗号分隔">
                            <div class="form-text text-muted mt-2">
                                请用逗号分隔多个参会人。
                            </div>
                        </div>
                        <div class="mb-3">
                            <label for="subject" class="form-label required">会议主题：</label>
                            <input class="form-control" type="text" id="subject" name="subject" required>
                            <div class="form-text text-muted mt-2">
                                请提供会议主题。
                            </div>
                        </div>
                        <div class="d-grid">
                            <button type="submit" class="btn btn-success w-50 mx-auto">上传文件</button>
                        </div>
                    </form>
                </div>
            </div>
            <footer class="mt-4 text-center text-muted">
                <p>Powered by Flask & Bootstrap</p>
            </footer>
        </div>

        <!-- 模态框：错误提示 -->
        <div class="modal fade" id="errorModal" tabindex="-1" aria-labelledby="errorModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header bg-danger text-white">
                        <h5 class="modal-title" id="errorModalLabel">错误</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        不支持的文件格式！请上传以下格式的文件：wav, mp3, m4a, flv, mp4, wma。
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- 模态框：成功提示 -->
        {% if success %}
        <script>
            window.onload = function() {
                const successModal = new bootstrap.Modal(document.getElementById('successModal'));
                successModal.show();
                successModal._element.addEventListener('hidden.bs.modal', clearUrlParams);
            }
        </script>
        <div class="modal fade" id="successModal" tabindex="-1" aria-labelledby="successModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header bg-success text-white">
                        <h5 class="modal-title" id="successModalLabel">上传成功</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        文件已成功上传，请检查您的邮箱。
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" onclick="clearFileInput()">关闭</button>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    ''', success=success, taskid=str(uuid.uuid4()))  # 生成唯一的taskid


# 上传文件的处理逻辑
@app.route('/upload', methods=['POST'])
def upload_file():
    logger.info("Get upload file.")
    if 'file' not in request.files or 'email' not in request.form:
        return redirect(url_for('upload_form'))

    file = request.files['file']
    email = request.form['email']  # 获取邮箱地址
    participants = request.form.get('participants', '')  # 获取参会人
    subject = request.form.get('subject', '')  # 获取会议主题
    taskid = request.form['taskid']  # 获取taskid

    logger.info("Get upload file filename: %s, email: %s, taskid: %s", file.filename, email, taskid)

    if file.filename == '':
        return redirect(url_for('upload_form'))

    # 检查文件格式是否符合要求
    if not allowed_file(file.filename):
        return redirect(url_for('upload_form'))

    # 生成唯一文件名
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # 上传到OSS
    oss.upload_to_oss("../config.ini", "ap-ai01", file.filename, file.filename)
    download_url = oss.get_download_url("../config.ini", "ap-ai01", file.filename, file.filename)
    logger.info("Upload to oss %s", download_url)
    time.sleep(5)

    # AI解析视频文件
    processor = SpeechToTextMeetingProcessor(config_path="../config.ini")
    # 处理新的音频文件
    processor.process_meeting_audio(download_url)
    util = Util()
    util.init()
    util.send_email(email, "会议纪要", "这是根据您上传视频声生成的会议纪要，请查收。", "./result.docx")

    # 存储邮箱和文件信息
    uploaded_files[taskid] = {
        'email': email,
        'participants': participants.split(','),
        'subject': subject,
        'original_filename': file.filename,
        'download_url': download_url,
    }

    logger.info("Uploaded files dict: %s", uploaded_files)

    return redirect(url_for('upload_form', success='true'))


if __name__ == '__main__':
    app.run(debug=True)
