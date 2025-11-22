import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image

# === CÁC HẰNG SỐ CẦN IMPORT ===

# 1. Đường dẫn tuyệt đối đến thư mục 'static/uploads'
# os.path.dirname(__file__) = thư mục hiện tại của file utils.py
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')

# 2. Giới hạn kích thước file upload (ví dụ: 16MB)
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# 3. Các đuôi file ảnh được phép
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Kiểm tra file có extension hợp lệ không"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# === HÀM QUAN TRỌNG CẦN IMPORT ===

def save_image_safely(file_storage, upload_folder):
    """
    Lưu file một cách an toàn:
    1. Kiểm tra extension.
    2. Tạo tên file duy nhất.
    3. Xác thực đó là ảnh thật (dùng Pillow).
    4. Trả về URL tương đối cho web.
    """
    if not file_storage or not allowed_file(file_storage.filename):
        return None # Không phải file hợp lệ

    try:
        # 1. Tạo tên file an toàn và duy nhất
        filename = secure_filename(file_storage.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        # Dùng UUID để tạo tên file không bao giờ trùng
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        save_path = os.path.join(upload_folder, unique_filename)

        # 2. Lưu file vào đường dẫn
        file_storage.save(save_path)

        # 3. Xác thực file là ảnh thật (rất quan trọng)
        #    Việc này ngăn chặn ai đó đổi tên file .exe thành .jpg
        try:
            with Image.open(save_path) as img:
                img.verify() # Kiểm tra xem đây có phải file ảnh không
        except Exception as img_err:
            os.remove(save_path) # Xóa file rác nếu không phải ảnh
            print(f"Lỗi xác thực ảnh: {img_err}")
            return None

        # 4. Trả về URL tương đối mà HTML/JS có thể dùng
        #    (ví dụ: 'static/uploads/tên_file_duy_nhat.jpg')
        return os.path.join('static', 'uploads', unique_filename).replace("\\", "/")

    except Exception as e:
        print(f"Lỗi khi lưu ảnh: {e}")
        return None