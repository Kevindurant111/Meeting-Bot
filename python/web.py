from flask import Flask, request, render_template_string, redirect, url_for
import os

app = Flask(__name__)

# 设置文件上传的保存路径
UPLOAD_FOLDER = '../upload'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # 确保上传文件夹存在
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 支持的文件格式
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'flv', 'mp4', 'wma'}


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
        <title>文件上传</title>
        <!-- 引入 Bootstrap -->
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <script>
            // 在客户端检查文件格式
            function validateFile() {
                const allowedExtensions = ['wav', 'mp3', 'm4a', 'flv', 'mp4', 'wma'];
                const fileInput = document.getElementById('file');
                const filePath = fileInput.value;
                const fileExtension = filePath.split('.').pop().toLowerCase();

                if (!allowedExtensions.includes(fileExtension)) {
                    // 显示模态框提示不支持的文件格式
                    const modal = new bootstrap.Modal(document.getElementById('errorModal'));
                    modal.show();
                    fileInput.value = ''; // 清空文件输入框
                    return false;
                }
                return true;
            }

            // 清空文件输入框
            function clearFileInput() {
                document.getElementById('file').value = '';
            }

            // 清除 URL 参数
            function clearUrlParams() {
                const url = new URL(window.location.href);
                url.searchParams.delete('success'); // 删除 success 参数
                window.history.replaceState({}, document.title, url); // 更新浏览器地址栏
            }
        </script>
    </head>
    <body>
        <div class="container mt-5">
            <div class="card shadow-sm">
                <div class="card-header bg-primary text-white">
                    <h3 class="card-title text-center">文件上传</h3>
                </div>
                <div class="card-body">
                    <form method="post" action="/upload" enctype="multipart/form-data" onsubmit="return validateFile()">
                        <div class="mb-3">
                            <label for="file" class="form-label">选择文件：</label>
                            <input class="form-control" type="file" id="file" name="file" required>
                            <div class="form-text text-muted mt-2">
                                支持的文件格式：<strong>wav, mp3, m4a, flv, mp4, wma</strong>
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
            // 显示成功模态框
            window.onload = function() {
                const successModal = new bootstrap.Modal(document.getElementById('successModal'));
                successModal.show();

                // 清除 URL 参数
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
                        文件已成功上传！
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" onclick="clearFileInput()">关闭</button>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- 引入 Bootstrap 的 JS -->
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    ''', success=success)


# 上传文件的处理逻辑
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('upload_form'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('upload_form'))

    # 检查文件格式是否符合要求
    if not allowed_file(file.filename):
        return redirect(url_for('upload_form'))

    # 保存文件
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    return redirect(url_for('upload_form', success='true'))


if __name__ == '__main__':
    app.run(debug=True)