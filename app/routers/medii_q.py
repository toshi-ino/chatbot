from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.medii_q import BaseRequest, DbEvidenceRequirementsResponse, PubMedQueryResponse
from app.services.langsmith_service import LangSmithService, get_langsmith_service
from app.services.llm_service import AssistantResponseService, DbEvidenceRequirementService, PubMedQueryService

router = APIRouter()

# NOTE：router内で直接依存性注入するとエラーが出るため、Dependsを別で定義しています
langsmith_dependency = Depends(get_langsmith_service)


@router.post("/pubmed-query", response_model=PubMedQueryResponse)
async def generate_pubmed_query(request: BaseRequest, langsmith_service: LangSmithService = langsmith_dependency):
    """PubMedの検索クエリを生成する"""
    try:
        service = PubMedQueryService(langsmith_service=langsmith_service)
        pubmed_query = service.generate_pubmed_query(request.thread_id, request.message_log, request.new_message)
        return PubMedQueryResponse(pubmed_query=pubmed_query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/db-evidence-requirement", response_model=DbEvidenceRequirementsResponse)
async def judge_db_evidence_requirements(request: BaseRequest, langsmith_service: LangSmithService = langsmith_dependency):
    """論文データベース検索の必要性を判定する"""
    try:
        service = DbEvidenceRequirementService(langsmith_service=langsmith_service)
        judgment = service.judge_db_evidence_requirement(request.thread_id, request.message_log, request.new_message)
        return DbEvidenceRequirementsResponse(result=judgment)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/assistant-response")
async def generate_streaming_assistant_response(request: BaseRequest, langsmith_service: LangSmithService = langsmith_dependency):
    """ストリーミングレスポンスを生成する"""
    try:
        service = AssistantResponseService(langsmith_service=langsmith_service)

        return StreamingResponse(
            service.generate_streaming_assistant_response(request.thread_id, request.message_log, request.new_message), media_type="text/plain"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
