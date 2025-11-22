import requests
from utils.config import COLAB_IMAGE_URL

def predict_image_service(upload_file):
    try:
        file_bytes = upload_file.file.read()

        files = {"file": (upload_file.filename, file_bytes, upload_file.content_type)}
        headers = {"Bypass-Tunnel-Reminder": "true"}

        response = requests.post(COLAB_IMAGE_URL, files=files, headers=headers)

        if response.status_code != 200:
            return {"error": f"Colab trả mã lỗi {response.status_code}"}

        ai_response = response.json()

        top5 = ai_response.get("top5", [])

        images = []
        scores = []

        for item in top5:
            # Nếu Colab trả base64
            if "image" in item:
                images.append(item["image"])

            # Nếu Colab trả path → convert sang base64 tại backend
            elif "path" in item:
                try:
                    import base64
                    import cv2

                    img = cv2.imread(item["path"])
                    _, buf = cv2.imencode(".jpg", img)
                    b64 = base64.b64encode(buf).decode()
                    images.append("data:image/jpeg;base64," + b64)
                except:
                    continue

            scores.append(item["score"])

        return {
            "text": "Dưới đây là Top 5 ảnh giống nhất!",
            "images": images,
            "scores": scores
        }

    except Exception as e:
        return {"error": f"Không thể kết nối AI Colab: {str(e)}"}
