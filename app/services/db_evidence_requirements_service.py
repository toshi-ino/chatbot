from fastapi import HTTPException

from app.api.schemas.schemas import BaseRequest, JudgeResponse
from app.services.llm_service import create_chat_prompt, get_llm

ASSIST_JUDGE_PROMPT = """
## 指示
- あなたは医学分野の専門家です。
- あなたはサービス内のAIエージェントの総合窓口として、「回答に必要な要素の判定」を行います。
- ユーザーの会話の履歴と最新のメッセージを入力します

## 回答に必要な要素の判定
- 過去の履歴を考慮しつつ、最新のメッセージについて「論文データベースの検索」が必要か否かを判定してください。
  - ユーザーにとってエビデンスは非常に重要です。
  - 医療に関連する質問だった場合にはデータベースの検索が**必須**です。
  - 過去に参照した論文であっても再度参照するようにしてください

## 出力の形式
- 出力には判定結果以外のメッセージは**一切記入しない**でください

### 回答に必要な要素の判定結果
- 「論文データベースの検索」が必要であると判断した場合は[DB_EVIDENCE:NEED]を返してください
- 「論文データベースの検索」が不要であると判断した場合は[DB_EVIDENCE:NOT]を返してください
"""


async def judge_db_evidence_requirement(request: BaseRequest) -> JudgeResponse:
    """
    データベースエビデンスが必要かどうかを判定する

    Args:
        request: ユーザーからのリクエスト

    Returns:
        JudgeResponse: 判定結果 ([DB_EVIDENCE:NEED] または [DB_EVIDENCE:NOT])

    Raises:
        HTTPException: LLM処理中にエラーが発生した場合
    """
    try:
        llm = get_llm(model_name="gpt-4o-mini", temperature=0.7)
        # message_logを辞書のリストに変換
        message_log = [{"role": msg.role, "content": msg.content} for msg in request.message_log]
        message_log.append({"role": "user", "content": request.new_message})

        prompt = create_chat_prompt(ASSIST_JUDGE_PROMPT, message_log)
        chain = prompt | llm
        response = chain.invoke({})

        result = str(response.content).strip()
        return JudgeResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

