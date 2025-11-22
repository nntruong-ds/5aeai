from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse
from services.image_service import predict_image_service

router = APIRouter(prefix="/api")  # <-- thêm /api

@router.post("/predict-image")
async def predict_image(
    query: str = Form(""),
    file: UploadFile = File(None)
):
    return predict_image_service(file)

@router.get("/get-image")
async def get_image(path: str):
    return FileResponse(path)
