from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.api.schemas.schemas import BaseRequest
from app.services.llm_service import get_llm, create_chat_prompt
from langchain.schema.messages import HumanMessage, AIMessage
from typing import List, Dict, Any

router = APIRouter()

ASSISTANT_PROMPT = """
あなたは医学分野の専門家です。ユーザーの医療に関する質問に対して、科学的根拠に基づいた回答を提供します。  
入力に論文情報が付随している場合はそれを参考にして、質問に対する包括的な回答を作成してください。  

## 禁止事項
- 論文本文からの **直接引用** 部分を除き、「**提案**」および「**推奨**」という語を使用しない。  
- 臨床データ等の根拠を示す際に、「PMIDの具体的な番号は提供されていませんが、最新のエビデンスに基づく情報です」と記載しない。  

## 指示
1. 論文情報が提供された場合はそれに基づいて回答を構成すること
2. 可能な限り最新のエビデンスに基づいて治療方針を提案すること
3. 異なる見解がある場合は、それぞれの立場とその根拠を説明すること
4. 回答には、参照した論文のPMIDを含めること
    * PMIDを含める場合、形式は**必ず**"PMID:{{PMID}}"にすること
    * "PMID:"部分の省略は表示ができなくなるため禁止
5. 患者の個別状況によって治療方針が異なる可能性があることを明記すること
6. 医学専門用語を使用する場合は、簡潔な説明を加えること
7. 提示された論文に情報が不足している場合は、その旨を明記すること
8. 「入力されていないPMID」を出力に含めることは禁止

## 出力形式
- 回答は日本語で提供してください。
- まずは結論と要約を述べてください。
    * タイトルは「要約」としてください。
- その後、**文献に基づく治療方針の概要** を示してください。  
- 臨床データ等の根拠を示してください。
- 回答には、この内容を必ず記載してください
    * 本回答は情報提供を目的としているため、最終的な診断や治療方針の決定は主治医の判断に委ねられます。
    * 新規治療薬や治療法に関するエビデンスは日々更新されるため、最新の文献・ガイドラインに基づいた判断と定期的な再評価が必要となります。

### 技術的注意
- 応答メッセージは、Markdown形式で提供する。ただし、「```markdown」等の記述は不要。
- あなたの回答でユーザーが疑問を解決できそうだと判断した場合、メッセージの末尾に"<<COMPLETED>>"タグを追記する
- 表示の際、記号が文字化けすることがあるので留意して出力してください(react-markdownで表示しています)
"""

@router.post("/assistant-response")
async def assistant_response(request: BaseRequest):
    try:
        llm = get_llm()
        
        # メッセージリストを作成
        message_log = [{"role": msg.role, "content": msg.content} for msg in request.message_log]
        message_log.append({"role": "user", "content": request.new_message})
        
        # プロンプトを設定
        prompt = create_chat_prompt(ASSISTANT_PROMPT, message_log)
        chain = prompt | llm

        async def generate():
            try:
                async for chunk in chain.astream({}):
                    if hasattr(chunk, 'content') and chunk.content:
                        yield chunk.content.encode('utf-8')
            except Exception as e:
                print(f"Streaming error: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

        return StreamingResponse(
            generate(),
            media_type="text/plain; charset=utf-8"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 