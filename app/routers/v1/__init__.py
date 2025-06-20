from fastapi import APIRouter

from .medii_q import router as medii_q_router

# v1 APIルーターを作成
v1_router = APIRouter()

# 各サブルーターを登録
v1_router.include_router(medii_q_router, tags=["medii_q"])
