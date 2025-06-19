from functools import lru_cache
from typing import Optional

from langsmith import Client

from app.core.config import get_settings


class LangSmithService:
    """LangSmith関連のサービス機能を提供するクラス"""

    def __init__(self):
        self.settings = get_settings()
        self.client = None

        # LangSmithクライアントを初期化（APIキーがある場合のみ）
        if self.settings.LANGSMITH_API_KEY:
            self.client = Client(api_key=self.settings.LANGSMITH_API_KEY)

    def get_prompt_and_model_from_langsmith(self, prompt_name: str, fallback_prompt: str) -> tuple[str, Optional[str], Optional[float]]:
        """
        LangSmithからプロンプトとモデル情報を取得する

        Args:
            prompt_name: LangSmithのプロンプト名
            fallback_prompt: 取得に失敗した場合のフォールバックプロンプト

        Returns:
            tuple:
                - prompt_template (str): プロンプトテンプレート文字列
                - model_name (str | None): モデル名（取得できない場合はNone）
                - temperature (float | None): temperature（取得できない場合はNone）
        """
        if self.client is not None:
            try:
                prompt_data = self.client.pull_prompt(prompt_name, include_model=True)

                prompt_template = fallback_prompt
                model_name = None
                temperature = None

                # プロンプトテンプレートの取得
                if hasattr(prompt_data, "first"):
                    first = prompt_data.first
                    if hasattr(first, "messages") and first.messages:
                        first_message = first.messages[0]
                        if hasattr(first_message, "prompt") and hasattr(first_message.prompt, "template"):
                            prompt_template = first_message.prompt.template

                # モデル情報の取得
                if hasattr(prompt_data, "last") and hasattr(prompt_data.last, "bound"):
                    bound = prompt_data.last.bound
                    model_name = getattr(bound, "model_name", None)
                    temperature = getattr(bound, "temperature", None)

                return prompt_template, model_name, temperature

            except Exception as e:
                print(f"LangSmithからプロンプト({prompt_name})取得時にエラーが発生しました。: {e}")
                return fallback_prompt, None, None

        print("LangsmithのClientが存在しません。")
        return fallback_prompt, None, None


@lru_cache
def get_langsmith_service() -> LangSmithService:
    """
    LangSmithServiceのシングルトンインスタンスを取得する

    Returns:
        LangSmithService: LangSmithServiceのシングルトンインスタンス
    """
    return LangSmithService()
