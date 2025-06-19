from fastapi import APIRouter

from app.api.schemas.schemas import BaseRequest, JudgeResponse
from app.services.db_evidence_requirements_service import judge_db_evidence_requirement

router = APIRouter()


@router.post("/db_evidence_requirements", response_model=JudgeResponse)
async def judge_db_evidence_requirement_endpoint(request: BaseRequest):
    """
    データベースエビデンスが必要かどうかを判定するエンドポイント

    Args:
        request: ユーザーからのリクエスト

    Returns:
        JudgeResponse: 判定結果 ([DB_EVIDENCE:NEED] または [DB_EVIDENCE:NOT])
    """
    return await judge_db_evidence_requirement(request)
