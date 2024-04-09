from agency_swarm.tools import BaseTool
from pydantic import Field
import os
from newsapi import NewsApiClient

api_key = os.getenv("NEWS_API_KEY")

class CryptoNewsExtractor(BaseTool):
    """
    A tool to extract and compile significant news related to cryptocurrencies. This tool utilizes the NewsAPI to search for recent news articles about cryptocurrencies. 
    """

    query: str = Field(
        ..., description="Query string to search for news, e.g., 'Bitcoin' or 'Ethereum'."
    )
    language: str = Field(
        ..., description="The language of the news articles, e.g., 'en' for English."
    )
    sort_by: str = Field(
        ..., description="Criteria for sorting the news articles, e.g., 'publishedAt' for most recent."
    )

    def run(self):
        newsapi = NewsApiClient(api_key=api_key)
        all_articles = newsapi.get_everything(q=self.query, language=self.language, sort_by=self.sort_by)
        return all_articles
