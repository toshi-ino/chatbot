from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.api.schemas.schemas import BaseRequest, JudgeResponse, PubMedQueryResponse
from app.services.llm_service import AssistantResponseService, DbEvidenceRequirementsService, PubMedQueryService

router = APIRouter()


@router.post("/pubmed-query", response_model=PubMedQueryResponse)
async def generate_pubmed_query(request: BaseRequest):
    """PubMedの検索クエリを生成する"""
    try:
        service = PubMedQueryService()
        pubmed_query = service.generate_pubmed_query(request.message_log, request.new_message)
        return PubMedQueryResponse(pubmed_query=pubmed_query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/db_evidence_requirements", response_model=JudgeResponse)
async def judge_db_evidence_requirement(request: BaseRequest):
    """PubMedの論文検索が必要かどうか判定する"""
    try:
        service = DbEvidenceRequirementsService()
        result = service.judge_db_evidence_requirement(request.message_log, request.new_message)
        return JudgeResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/assistant-response")
async def assistant_response(request: BaseRequest):
    """medii_qの回答を生成する"""
    try:
        service = AssistantResponseService()

        async def generate():
            try:
                async for chunk in service.generate_streaming_response(
                    request.message_log,
                    request.new_message,
                    model_name="gpt-4o-mini",  # TODO: モデルをo3に変更すること
                    temperature=0.7,
                ):
                    yield chunk
            except Exception as e:
                print(f"Streaming error: {e!s}")
                raise HTTPException(status_code=500, detail=str(e)) from e

        return StreamingResponse(generate(), media_type="text/plain; charset=utf-8")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
