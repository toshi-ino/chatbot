from abc import ABC, abstractmethod

from langchain.prompts import ChatPromptTemplate
from langchain.schema.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.api.schemas.schemas import Message
from app.core.config import get_settings

settings = get_settings()


def get_llm(model_name: str = settings.DEFAULT_MODEL_NAME, temperature: float = settings.DEFAULT_TEMPERATURE):
    return ChatOpenAI(model=model_name, temperature=temperature, streaming=True)


def create_prompt_messages(system_prompt: str, messages: list):
    prompt_messages: list = [SystemMessage(content=system_prompt)]

    for msg in messages:
        if msg["role"] == "user":
            prompt_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            prompt_messages.append(AIMessage(content=msg["content"]))

    return ChatPromptTemplate.from_messages(prompt_messages)


class BaseLLMService(ABC):
    """プロンプトベースのLLM処理を行う抽象基底クラス"""

    @property
    @abstractmethod
    def prompt_template(self) -> str:
        pass

    def process_message(self, message_log: list[Message], new_message: str, model_name: str, temperature: float) -> str:
        llm = get_llm(model_name=model_name, temperature=temperature)
        message_log_dict = [{"role": msg.role, "content": msg.content} for msg in message_log]
        message_log_dict.append({"role": "user", "content": new_message})

        prompt = create_prompt_messages(self.prompt_template, message_log_dict)
        chain = prompt | llm
        response = chain.invoke({})
        return str(response.content).strip()

    async def generate_streaming_response(self, message_log: list[Message], new_message: str, model_name: str, temperature: float):
        """
        メッセージからストリーミングレスポンスを生成する汎用メソッド

        Args:
            message_log: メッセージ履歴のリスト
            new_message: 新しいメッセージ
            model_name: 使用するLLMモデル名（デフォルト: gpt-4o-mini）
            temperature: LLMの温度パラメータ（デフォルト: 0.7）

        Yields:
            bytes: ストリーミングレスポンスのチャンク
        """
        llm = get_llm(model_name=model_name, temperature=temperature)

        # メッセージリストを作成
        message_log_dict = [{"role": msg.role, "content": msg.content} for msg in message_log]
        message_log_dict.append({"role": "user", "content": new_message})

        prompt = create_prompt_messages(self.prompt_template, message_log_dict)
        chain = prompt | llm

        async for chunk in chain.astream({}):
            if hasattr(chunk, "content") and chunk.content:
                yield str(chunk.content).encode("utf-8")


class PubMedQueryService(BaseLLMService):
    @property
    def prompt_template(self) -> str:
        return """
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
   - 上記フォーマット外のテキスト(説明・理由・参考情報など)は **絶対に書かない**。
"""

    def generate_pubmed_query(self, message_log: list[Message], new_message: str) -> str:
        """
        メッセージからPubMedクエリを生成する

        Args:
            message_log: メッセージ履歴のリスト
            new_message: 新しいメッセージ

        Returns:
            str: 生成されたPubMedクエリ
        """
        return self.process_message(message_log, new_message, model_name="gpt-4o-mini", temperature=0.7)


class DbEvidenceRequirementsService(BaseLLMService):
    @property
    def prompt_template(self) -> str:
        return """
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

    def judge_db_evidence_requirement(self, message_log: list[Message], new_message: str) -> str:
        """
        メッセージ履歴と新しいメッセージから論文データベース検索の必要性を判定する

        Args:
            message_log: メッセージ履歴のリスト
            new_message: 新しいメッセージ

        Returns:
            str: 判定結果 ([DB_EVIDENCE:NEED] または [DB_EVIDENCE:NOT])
        """
        return self.process_message(message_log, new_message, model_name="gpt-4o-mini", temperature=0.7)


class AssistantResponseService(BaseLLMService):
    @property
    def prompt_template(self) -> str:
        return """
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

    async def generate_streaming_assistant_response(self, message_log: list[Message], new_message: str):
        """
        アシスタント回答のストリーミングレスポンスを生成する

        Args:
            message_log: メッセージ履歴のリスト
            new_message: 新しいメッセージ

        Yields:
            bytes: ストリーミングレスポンスのチャンク
        """
        async for chunk in self.generate_streaming_response(message_log, new_message, model_name="gpt-4o-mini", temperature=0.7):
            yield chunk
