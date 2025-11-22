from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.image_route import router as image_router

app = FastAPI()

# CHO PHÉP FRONTEND CALL BACKEND
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # hoặc ["http://127.0.0.1:5000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(image_router)
