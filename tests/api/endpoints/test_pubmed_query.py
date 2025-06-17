import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_pubmed_query_endpoint():
    # テスト用のリクエストデータ
    request_data = {
        "new_message": "diabetes treatment",
        "message_log": [
            {"role": "user", "content": "diabetes treatment"}
        ],
        "max_results": 5
    }
    
    # エンドポイントにリクエストを送信
    response = client.post("/api/v1/pubmed-query", json=request_data)
    
    # レスポンスの検証
    assert response.status_code == 200
    assert "pubmed_query" in response.json()
    assert isinstance(response.json()["pubmed_query"], str)
    assert len(response.json()["pubmed_query"]) > 0

def test_pubmed_query_endpoint_with_empty_query():
    # 空のクエリでテスト
    request_data = {
        "new_message": "",
        "message_log": [],
        "max_results": 5
    }
    
    response = client.post("/api/v1/pubmed-query", json=request_data)
    assert response.status_code == 200
    assert "pubmed_query" in response.json()
    assert isinstance(response.json()["pubmed_query"], str)

def test_pubmed_query_endpoint_with_invalid_max_results():
    # 無効なmax_resultsでテスト
    request_data = {
        "new_message": "diabetes",
        "message_log": [
            {"role": "user", "content": "diabetes"}
        ],
        "max_results": -1
    }
    
    response = client.post("/api/v1/pubmed-query", json=request_data)
    assert response.status_code == 200
    assert "pubmed_query" in response.json()
    assert isinstance(response.json()["pubmed_query"], str)

def test_pubmed_query_endpoint_with_large_max_results():
    # 大きなmax_resultsでテスト
    request_data = {
        "new_message": "diabetes",
        "message_log": [
            {"role": "user", "content": "diabetes"}
        ],
        "max_results": 100
    }
    
    response = client.post("/api/v1/pubmed-query", json=request_data)
    assert response.status_code == 200
    assert "pubmed_query" in response.json()
    assert isinstance(response.json()["pubmed_query"], str)
    assert len(response.json()["pubmed_query"]) > 0 