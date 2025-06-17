from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import assistant_response, db_evidence_requirements, pubmed_query
from app.core.config import get_settings

# ルートの .env を読み込む
load_dotenv()

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの登録
app.include_router(pubmed_query.router, prefix="/api", tags=["pubmed_query"])
app.include_router(db_evidence_requirements.router, prefix="/api", tags=["db_evidence"])
app.include_router(assistant_response.router, prefix="/api", tags=["assistant_response"])

@app.get("/")
async def root():
    return {"message": "AI API is running"}
