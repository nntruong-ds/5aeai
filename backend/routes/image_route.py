from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import Optional
from services.image_service import predict_image_service

router = APIRouter(prefix="/api")

@router.post("/predict-image")
async def predict_image(
    query: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    alpha: float = Form(0.5)
):
    # Kiểm tra: Phải có ít nhất ảnh hoặc text
    if not query and not file:
        return {"error": "Vui lòng nhập văn bản hoặc tải ảnh lên!"}

    return predict_image_service(file, query, alpha)

@router.get("/get-image")
async def get_image(path: str):
    return FileResponse(path)
