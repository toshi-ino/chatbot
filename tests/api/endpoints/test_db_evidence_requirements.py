import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.schemas.schemas import BaseRequest, Message

client = TestClient(app)

def test_db_evidence_requirements_endpoint():
    # テスト用のリクエストデータ
    request_data = {
        "new_message": "糖尿病の治療法について教えてください",
        "message_log": [
            {
                "role": "user",
                "content": "糖尿病の治療法について教えてください"
            }
        ]
    }
    
    # エンドポイントにリクエストを送信
    response = client.post("/api/v1/db_evidence_requirements", json=request_data)
    
    # レスポンスの検証
    assert response.status_code == 200
    assert "result" in response.json()
    assert response.json()["result"] in ["[DB_EVIDENCE:NEED]", "[DB_EVIDENCE:NOT]"]

def test_db_evidence_requirements_endpoint_with_empty_message():
    # 空のメッセージログでテスト
    request_data = {
        "new_message": "",
        "message_log": []
    }
    
    response = client.post("/api/v1/db_evidence_requirements", json=request_data)
    assert response.status_code == 200
    assert "result" in response.json()

def test_db_evidence_requirements_endpoint_with_non_medical_query():
    # 医療に関連しない質問でテスト
    request_data = {
        "new_message": "今日の天気はどうですか？",
        "message_log": [
            {
                "role": "user",
                "content": "今日の天気はどうですか？"
            }
        ]
    }
    
    response = client.post("/api/v1/db_evidence_requirements", json=request_data)
    assert response.status_code == 200
    assert "result" in response.json()
    assert response.json()["result"] == "[DB_EVIDENCE:NOT]"

def test_db_evidence_requirements_endpoint_with_medical_query():
    # 医療に関連する質問でテスト
    request_data = {
        "new_message": "高血圧の最新の治療法について教えてください",
        "message_log": [
            {
                "role": "user",
                "content": "高血圧の最新の治療法について教えてください"
            }
        ]
    }
    
    response = client.post("/api/v1/db_evidence_requirements", json=request_data)
    assert response.status_code == 200
    assert "result" in response.json()
    assert response.json()["result"] == "[DB_EVIDENCE:NEED]" 