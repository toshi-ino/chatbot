from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers import medii_q

# ルートの .env を読み込む
load_dotenv()

settings = get_settings()

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの登録
app.include_router(medii_q.router, prefix="/api", tags=["medii_q"])


# 疎通確認用のエンドポイント
@app.get("/")
async def root():
    return {"message": "AI API is running"}
