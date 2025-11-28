import requests
from utils.config import COLAB_IMAGE_URL

def predict_image_service(upload_file=None, text_query=None, alpha=0.5):
    try:
        files = None
        # Chỉ tạo payload file nếu người dùng có upload ảnh
        if upload_file:
            upload_file.file.seek(0)
            file_bytes = upload_file.file.read()
            files = {"file": (upload_file.filename, file_bytes, upload_file.content_type)}

        # Gửi kèm text query và alpha dưới dạng form data
        data = {
            "query": text_query if text_query else "",
            "alpha": alpha
        }

        headers = {"Bypass-Tunnel-Reminder": "true"}

        # Gửi request sang Colab (Ngrok)
        # requests.post sẽ tự động xử lý multipart/form-data khi có 'files' hoặc 'data'
        response = requests.post(COLAB_IMAGE_URL, files=files, data=data, headers=headers)

        if response.status_code != 200:
            return {"error": f"Colab trả mã lỗi {response.status_code}"}

        ai_response = response.json()

        # Xử lý kết quả trả về (tương thích với format json của server Colab mới)
        top5 = ai_response.get("top5", [])

        images = []
        scores = []

        for item in top5:
            if "image" in item:
                images.append(item["image"])
            scores.append(item.get("score", 0))

        return {
            "text": "Dưới đây là Top 5 ảnh giống nhất!",
            "images": images,
            "scores": scores
        }

    except Exception as e:
        print(f"Lỗi backend: {str(e)}")
        return {"error": f"Không thể kết nối AI Colab: {str(e)}"}
