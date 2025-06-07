from flask import Flask, render_template_string, request, send_from_directory, redirect, url_for
import os
import qrcode
from io import BytesIO
import base64

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
copyright = "© ADEL MRAKKEN 2025 - All rights reserved"
# HTML Template with Enhanced CSS
INDEX_HTML = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نقل الملفات عبر QR</title>
    <style>
        :root {
            --primary-color: #4CAF50;
            --secondary-color: #f8f9fa;
            --accent-color: #2196F3;
            --text-color: #333;
            --error-color: #f44336;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background-color: #f5f5f5;
            color: var(--text-color);
            line-height: 1.6;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        h1 {
            color: var(--primary-color);
            margin-bottom: 20px;
            text-align: center;
        }
        
        h2 {
            color: var(--accent-color);
            margin: 25px 0 15px;
            border-bottom: 2px solid #eee;
            padding-bottom: 8px;
        }
        
        .qr-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin: 20px 0;
        }
        
        .qr-code {
            width: 200px;
            height: 200px;
            border: 1px solid #ddd;
            padding: 10px;
            background: white;
        }
        
        .server-url {
            margin: 15px 0;
            font-size: 18px;
            word-break: break-all;
            text-align: center;
        }
        
        .server-url a {
            color: var(--accent-color);
            text-decoration: none;
        }
        
        .server-url a:hover {
            text-decoration: underline;
        }
        
        .upload-form {
            display: flex;
            flex-direction: column;
            gap: 15px;
            margin: 20px 0;
        }
        
        .file-input {
            padding: 12px;
            border: 2px dashed #ccc;
            border-radius: 5px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .file-input:hover {
            border-color: var(--accent-color);
            background: #f0f8ff;
        }
        
        .btn {
            background-color: var(--primary-color);
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
        }
        
        .btn:hover {
            background-color: #45a049;
        }
        
        .btn-secondary {
            background-color: var(--accent-color);
        }
        
        .btn-secondary:hover {
            background-color: #0b7dda;
        }
        
        .file-list {
            list-style: none;
            margin: 20px 0;
        }
        
        .file-list li {
            padding: 10px;
            background: var(--secondary-color);
            margin-bottom: 8px;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .file-list a {
            color: var(--accent-color);
            text-decoration: none;
            flex-grow: 1;
        }
        
        .file-list a:hover {
            text-decoration: underline;
        }
        
        .back-link {
            display: inline-block;
            margin-top: 20px;
        }
        
        @media (max-width: 600px) {
            .container {
                padding: 15px;
            }
            
            h1 {
                font-size: 24px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>نقل الملفات عبر رمز الاستجابة السريعة</h1>
        
        <div class="qr-container">
            <img class="qr-code" src="data:image/png;base64,{{ qr_code }}" alt="QR Code">
            <div class="server-url">
                أو انتقل إلى: <a href="{{ server_url }}">{{ server_url }}</a>
            </div>
        </div>
        
        <h2>رفع ملف جديد</h2>
        <form class="upload-form" method="post" action="/upload" enctype="multipart/form-data">
            <input type="file" class="file-input" name="file" required>
            <button type="submit" class="btn">رفع الملف</button>
        </form>
        
        <h2>الملفات المتاحة</h2>
        <a href="/files" class="btn btn-secondary">عرض جميع الملفات</a>
    </div>
</body>
</html>
'''

FILES_HTML = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>الملفات المتاحة</title>
    <style>
        /* نفس CSS السابق */
        :root {
            --primary-color: #4CAF50;
            --secondary-color: #f8f9fa;
            --accent-color: #2196F3;
            --text-color: #333;
            --error-color: #f44336;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background-color: #f5f5f5;
            color: var(--text-color);
            line-height: 1.6;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        h1 {
            color: var(--primary-color);
            margin-bottom: 20px;
            text-align: center;
        }
        
        .file-list {
            list-style: none;
            margin: 20px 0;
        }
        
        .file-list li {
            padding: 12px 15px;
            background: var(--secondary-color);
            margin-bottom: 10px;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s;
        }
        
        .file-list li:hover {
            transform: translateX(-5px);
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .file-list a {
            color: var(--accent-color);
            text-decoration: none;
            flex-grow: 1;
        }
        
        .file-list a:hover {
            text-decoration: underline;
        }
        
        .back-link {
            display: inline-block;
            margin-top: 20px;
            text-align: center;
            width: 100%;
        }
        
        .btn {
            background-color: var(--primary-color);
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>الملفات المتاحة للتنزيل</h1>
        
        <ul class="file-list">
            {% for file in files %}
                <li>
                    <a href="/download/{{ file }}">{{ file }}</a>
                </li>
            {% endfor %}
        </ul>
        
        <div class="back-link">
            <a href="/" class="btn">العودة للصفحة الرئيسية</a>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    # احصل على IP الخادم تلقائياً (يتطلب إعداداً يدوياً في بعض الشبكات)
    ip_address = ""  # استبدلها بـ IP حاسوبك!
    port = 5000
    server_url = f"http://{ip_address}:{port}"
    
    # توليد QR Code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(server_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#2196F3", back_color="white")  # لون أزرق
    
    # تحويل الصورة إلى base64
    buffered = BytesIO()
    img.save(buffered)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return render_template_string(INDEX_HTML, qr_code=img_str, server_url=server_url)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect('/')
    file = request.files['file']
    if file.filename == '':
        return redirect('/')
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return redirect('/')

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
print(copyright)
@app.route('/files')
def list_files():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template_string(FILES_HTML, files=files)
app.config['DEBUG_TB_PANELS'] = ['flask_debugtoolbar.panels.timer.TimerDebugPanel']
app.config['SECRET_KEY'] = 'adel333'  # 🔑 يغير الـ PIN تلقائياً
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)