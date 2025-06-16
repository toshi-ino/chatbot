from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import pubmed_query, judge, assistant_response
from app.core.config import get_settings

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
app.include_router(pubmed_query.router, prefix="/api/v1", tags=["pubmed"])
app.include_router(judge.router, prefix="/api/v1", tags=["judge"])
app.include_router(assistant_response.router, prefix="/api/v1", tags=["assistant"])

@app.get("/")
async def root():
    return {"message": "Medical Chatbot API is running"} 