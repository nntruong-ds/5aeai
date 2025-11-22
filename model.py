# model.py
import random
# ## THAY ĐỔI: Thêm import cho AI thật (ví dụ: nếu dùng HuggingFace)
# from transformers import pipeline  # Uncomment và install transformers nếu cần

def process_search(query, image_urls):
    """
    Xử lý tìm kiếm bằng text + ảnh
    Sau này nhóm bạn thay bằng model AI thật (CLIP, BLIP, v.v.)
    Ví dụ tích hợp AI thật:
    # classifier = pipeline("zero-shot-image-classification", model="openai/clip-vit-large-patch14")
    # results = classifier(image_urls, candidate_labels=["mèo", "chó", query])
    # return results[0]['label'], []  # Trả text + images từ AI
    """
    if not query and not image_urls:
        return "Bạn chưa nhập gì cả.", []

    results = ["Đây là kết quả tìm kiếm của bạn! (Markdown: **bold** *italic*)", "Mình tìm thấy một số hình ảnh tương tự."]  # ## THAY ĐỔI: Thêm Markdown test
    images = [
        "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400",
        "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400"
    ]

    return random.choice(results), images[:random.randint(1, 2)]