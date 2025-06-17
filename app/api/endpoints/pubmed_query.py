from fastapi import APIRouter, HTTPException
from app.api.schemas.schemas import BaseRequest, PubMedQueryResponse
from app.services.llm_service import get_llm, create_chat_prompt

router = APIRouter()

PUBMED_QUERY_PROMPT = """
#プロンプト
あなたは医学分野に精通した検索エキスパートです。ユーザーの医療に関する質問から **PubMed 検索に最適なクエリ** を生成してください。  
**出力は指定の書式のみ** とし、それ以外の説明・注釈・空行・コードブロック・装飾は一切書かないでください。

### ✅ クエリ作成ルール
1. **PICO 抽出**  
   - 各要素 (Population / Intervention / Comparison / Outcome) を質問文から抽出。  
   - 不明または存在しない要素は省略するか、ワイルドカード * で代用。

2. **語彙とタグ付け**  
   - 各 PICO 要素に **必ず 1 つ以上の検索語** を割り当て、以下の優先順位でタグを付ける。  
     1. "XXXXX"[MeSH Terms]  
     2. XXXXX[Title/Abstract] または XXXXX[TIAB]  
   - **All Fields** は使用禁止。MeSH が無い場合も必ず [TIAB] を付ける。  
   - 同義語・関連語は括弧でまとめ (語A OR 語B …)。

3. **要素間の結合**  
   - PICO が異なる要素同士は **AND** で結合。必要なら **NOT** で除外語。  

4. **フィルタリング**  
   - 研究デザインや出版タイプを必要に応じて追加  
     例: "Randomized Controlled Trial"[Publication Type]  

5. **出力はクエリのみ**  
   - 上記フォーマット外のテキスト（説明・理由・参考情報など）は **絶対に書かない**。
"""

@router.post("/pubmed-query", response_model=PubMedQueryResponse)
async def generate_pubmed_query(request: BaseRequest):
    try:
        llm = get_llm(model_name="gpt-4o-mini", temperature=0.7)
        # message_logを辞書のリストに変換
        message_log = [{"role": msg.role, "content": msg.content} for msg in request.message_log]
        message_log.append({"role": "user", "content": request.new_message})

        prompt = create_chat_prompt(PUBMED_QUERY_PROMPT, message_log)
        chain = prompt | llm
        response = chain.invoke({})
        
        return PubMedQueryResponse(pubmed_query=response.content.strip())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 