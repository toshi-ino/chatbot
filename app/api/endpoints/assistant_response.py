from fastapi import APIRouter

from app.api.schemas.schemas import BaseRequest
from app.services.assistant_response_service import generate_assistant_response

router = APIRouter()


@router.post("/assistant-response")
async def assistant_response(request: BaseRequest):
    """
    アシスタントの応答を生成するエンドポイント

    Args:
        request: ユーザーからのリクエスト

    Returns:
        StreamingResponse: ストリーミング形式の応答
    """
    return await generate_assistant_response(request)
