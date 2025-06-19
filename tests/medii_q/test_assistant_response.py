from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# HTTPステータスコードの定数
HTTP_OK = 200


def test_assistant_response_endpoint():
    # テスト用のリクエストデータ
    request_data = {
        "new_message": "糖尿病の治療法について教えてください",
        "message_log": [{"role": "user", "content": "糖尿病の治療法について教えてください"}],
    }

    # エンドポイントにリクエストを送信
    response = client.post("/api/assistant-response", json=request_data)

    # レスポンスの検証
    assert response.status_code == HTTP_OK
    assert isinstance(response.text, str)
    assert len(response.text) > 0


def test_assistant_response_endpoint_with_empty_message():
    # 空のメッセージログでテスト
    request_data = {"new_message": "", "message_log": []}

    response = client.post("/api/assistant-response", json=request_data)
    assert response.status_code == HTTP_OK
    assert isinstance(response.text, str)


def test_assistant_response_endpoint_with_conversation_history():
    # 会話履歴を含むリクエストでテスト
    request_data = {
        "new_message": "治療法はありますか？",
        "message_log": [
            {"role": "user", "content": "糖尿病について教えてください"},
            {"role": "assistant", "content": "糖尿病は、血糖値が高くなる病気です。主な症状は..."},
            {"role": "user", "content": "治療法はありますか？"},
        ],
    }

    response = client.post("/api/assistant-response", json=request_data)
    assert response.status_code == HTTP_OK
    assert isinstance(response.text, str)
    assert len(response.text) > 0


def test_assistant_response_endpoint_with_medical_evidence():
    # 医学的エビデンスを含むリクエストでテスト
    request_data = {
        "new_message": "高血圧の最新の治療法について教えてください",
        "message_log": [
            {"role": "user", "content": "高血圧の最新の治療法について教えてください"},
            {"role": "assistant", "content": "最新の研究によると、以下の治療法が効果的です..."},
        ],
    }

    response = client.post("/api/assistant-response", json=request_data)
    assert response.status_code == HTTP_OK
    assert isinstance(response.text, str)
    assert len(response.text) > 0
