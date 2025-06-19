from functools import lru_cache

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

    def get_prompt_from_langsmith(self, prompt_name: str, fallback_prompt: str) -> str:
        """
        LangSmithからプロンプトを取得する

        Args:
            prompt_name: LangSmithのプロンプト名
            fallback_prompt: 取得に失敗した場合のフォールバックプロンプト

        Returns:
            str: プロンプトテンプレート文字列
        """
        if self.client is not None:
            try:
                prompt = self.client.pull_prompt(prompt_name)

                if hasattr(prompt, "messages") and prompt.messages:
                    first_message = prompt.messages[0]
                    template = getattr(first_message, "prompt", None)

                    if template and hasattr(template, "template"):
                        return template.template

                print(f"LangSmithからプロンプト({prompt_name})を取得できませんでした。")
                return fallback_prompt

            except Exception as e:
                print(f"LangSmithからプロンプト({prompt_name})取得時にエラーが発生しました。: {e}")
                return fallback_prompt

        print("LangsmithのClientが存在しません。")
        return fallback_prompt


@lru_cache
def get_langsmith_service() -> LangSmithService:
    """
    LangSmithServiceのシングルトンインスタンスを取得する

    Returns:
        LangSmithService: LangSmithServiceのシングルトンインスタンス
    """
    return LangSmithService()
