import os
import uuid
from flask import Flask, render_template, request, jsonify, make_response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Import các hàm xử lý từ file mới
from model import process_search
from utils import save_image_safely, UPLOAD_FOLDER, MAX_CONTENT_LENGTH

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Tạo thư mục uploads nếu chưa có
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Giới hạn request để tránh spam
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "30 per hour", "10 per minute"]
)

@app.route('/')
def index():
    """Render trang chủ (giao diện chat)."""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
@limiter.limit("5 per minute") # Giới hạn riêng cho API search
def search():
    try:
        query = request.form.get('query', '').strip()
        files = request.files.getlist('images')

        if not query and not files:
            return jsonify({"error": "Vui lòng nhập nội dung hoặc tải ảnh lên."}), 400

        # Gửi request sang FastAPI (backend AI)
        fastapi_url = "http://127.0.0.1:8000/api/predict-image"

        form_files = []
        for f in files:
            form_files.append(
                ('file', (f.filename, f.stream, f.content_type))
            )

        response = requests.post(fastapi_url, files=form_files)

        if response.status_code != 200:
            return jsonify({"error": "Backend AI lỗi, kiểm tra FastAPI."}), 500

        ai_data = response.json()

        return jsonify({
            "text": ai_data.get("text", ""),
            "images": ai_data.get("images", [])
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": "Lỗi máy chủ Flask."}), 500


@app.errorhandler(429)
def ratelimit_handler(e):
    """Xử lý lỗi khi bị rate limit."""
    return make_response(
        jsonify(error=f"Bạn đã gửi quá nhiều yêu cầu. Vui lòng thử lại sau: {e.description}"), 429
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
