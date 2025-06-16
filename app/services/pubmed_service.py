import requests
from typing import List, Dict
from app.core.config import get_settings

settings = get_settings()

class PubMedService:
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.db = "pubmed"
        self.retmode = "json"

    async def search_papers(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        PubMedで論文を検索し、PMIDとタイトルを取得する
        
        Args:
            query (str): 検索クエリ
            max_results (int): 取得する論文の最大数
            
        Returns:
            List[Dict]: PMIDとタイトルのリスト
        """
        # ESearchを使用してPMIDを取得
        search_url = f"{self.base_url}/esearch.fcgi"
        params = {
            "db": self.db,
            "term": query,
            "retmax": max_results,
            "retmode": self.retmode,
            "sort": "relevance"
        }
        
        response = requests.get(search_url, params=params)
        if response.status_code != 200:
            raise Exception("PubMed API request failed")
            
        data = response.json()
        pmids = data["esearchresult"]["idlist"]
        
        # EFetchを使用して論文の詳細情報を取得
        fetch_url = f"{self.base_url}/efetch.fcgi"
        params = {
            "db": self.db,
            "id": ",".join(pmids),
            "retmode": "xml"
        }
        
        response = requests.get(fetch_url, params=params)
        if response.status_code != 200:
            raise Exception("PubMed API request failed")
            
        # XMLレスポンスをパースして必要な情報を抽出
        # 注: 実際の実装ではXMLパースが必要
        papers = []
        for pmid in pmids:
            papers.append({
                "pmid": pmid,
                "title": "論文タイトル",  # 実際の実装ではXMLから抽出
                "abstract": "論文アブストラクト"  # 実際の実装ではXMLから抽出
            })
            
        return papers

    async def get_paper_details(self, pmid: str) -> Dict:
        """
        特定のPMIDの論文詳細を取得する
        
        Args:
            pmid (str): 論文のPMID
            
        Returns:
            Dict: 論文の詳細情報
        """
        fetch_url = f"{self.base_url}/efetch.fcgi"
        params = {
            "db": self.db,
            "id": pmid,
            "retmode": "xml"
        }
        
        response = requests.get(fetch_url, params=params)
        if response.status_code != 200:
            raise Exception("PubMed API request failed")
            
        # XMLレスポンスをパースして必要な情報を抽出
        # 注: 実際の実装ではXMLパースが必要
        return {
            "pmid": pmid,
            "title": "論文タイトル",  # 実際の実装ではXMLから抽出
            "abstract": "論文アブストラクト",  # 実際の実装ではXMLから抽出
            "authors": ["著者1", "著者2"],  # 実際の実装ではXMLから抽出
            "publication_date": "2024-01-01"  # 実際の実装ではXMLから抽出
        } 