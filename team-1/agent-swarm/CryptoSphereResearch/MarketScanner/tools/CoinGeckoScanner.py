from agency_swarm.tools import BaseTool
from pydantic import Field
import os
from pycoingecko import CoinGeckoAPI

api_url = "https://api.coingecko.com/api/v3"

class CoinGeckoScanner(BaseTool):
    """
    A tool to scan various cryptocurrency market data sources, specifically the CoinGecko API. It retrieves current data about cryptocurrencies including price movements and trading volumes. 
    """

    cryptocurrency: str = Field(
        ..., description="Symbol of the cryptocurrency to scan, e.g., 'btc' for Bitcoin."
    )
    currency: str = Field(
        ..., description="Fiat currency to display the crypto data in, e.g., 'usd'."
    )

    def run(self):
        cg = CoinGeckoAPI()
        data = cg.get_price(ids=self.cryptocurrency, vs_currencies=self.currency, include_market_cap='true', include_24hr_vol='true', include_24hr_change='true', include_last_updated_at='true')
        return data
