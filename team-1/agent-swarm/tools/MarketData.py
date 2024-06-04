import requests
import time

from pydantic import Field
from agency_swarm.tools import BaseTool

class MarketData(BaseTool):
    """
This tool uses the CoinGecko API to get and return market data information, 
including total market cap, top gainers and losers, and trading volume.
    """
    # Set API endpoint base URL
    api_base_url: str = Field(..., description="The CoinGecko API endpoint base URL")
    api_base_url = "https://api.coingecko.com/api/v3/"

    # Other parameters
    coin_ids: str = Field(..., description="Comma-separated list of coin identifiers, e.g., 'bitcoin,ethereum'")
    vs_currency: str = Field(..., description="The currency identifier, e.g., 'usd'")
    vs_currency = "usd"

    # Set rate limit and delay between requests
    rate_limit: int = Field(..., description="The rate limit for the CoinGecko API endpoints")
    rate_limit = 30  # 30 requests per minute for public API
    delay_between_requests: float = Field(..., description="The delay in seconds between requests to the CoinGecko API endpoints")
    delay_between_requests = 60 / rate_limit  # delay in seconds

    def handle_api_errors(self, response):
        # Handle API errors
        if response.status_code == 400:
            print("Bad Request. please check your request and try again.")
        elif response.status_code == 401:
            print("Unauthorized. Check your API key and credentials.")
        elif response.status_code == 403:
            print("Forbidden. Your access is blocked. Please contact CoinGecko support.")
        elif response.status_code == 429:
            print("Rate limit exceeded. Please reduce the number of requests or consider upgrading to a paid plan.")
        elif response.status_code == 500:
            print("Internal Server Error. Please try again later.")
        elif response.status_code == 503:
            print("Service Unavailable. Check the API status and updates on https://status.coingecko.com/")

    def make_api_request(self, url, params=None):
        # Make API request with rate limiting and error handling
        response = requests.get(url, params=params)
        if response.status_code != 200:
            self.handle_api_errors(response)
            return None
        time.sleep(self.delay_between_requests)  # respect rate limit
        return response.json()

    def get_total_market_cap(self):
        url = self.api_base_url + "global"
        data = self.make_api_request(url)
        if data:
            total_market_cap = data["data"]["total_market_cap"]["usd"]
            return total_market_cap
        return None

    def get_top_gainers(self, limit=10):
        url = self.api_base_url + "coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": limit,
            "page": 1
        }
        data = self.make_api_request(url, params)
        if data:
            top_gainers = []
            for coin in data:
                top_gainers.append({
                    "name": coin["name"],
                    "symbol": coin["symbol"],
                    "price_change_percentage_24h": coin["price_change_percentage_24h"]
                })
            return top_gainers
        return None

    def get_top_losers(self, limit=10):
        url = self.api_base_url + "coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_asc",
            "per_page": limit,
            "page": 1
        }
        data = self.make_api_request(url, params)
        if data:
            top_losers = []
            for coin in data:
                top_losers.append({
                    "name": coin["name"],
                    "symbol": coin["symbol"],
                    "price_change_percentage_24h": coin["price_change_percentage_24h"]
                })
            return top_losers
        return None

    def get_trading_volume(self, coin_ids, vs_currencies="usd"):
        url = self.api_base_url + "simple/price"
        params = {
            "ids": ",".join(coin_ids),
            "vs_currencies": vs_currencies,
            "include_24hr_vol": "true"
        }
        data = self.make_api_request(url, params)
        if data:
            trading_volume = {}
            for coin_id, volume in data.items():
                trading_volume[coin_id] = volume["usd_24h_vol"]
            return trading_volume
        return None

    def run(self):
        total_market_cap = self.get_total_market_cap()
        top_gainers = self.get_top_gainers()
        top_losers = self.get_top_losers()
        trading_volume = self.get_trading_volume(self.coin_ids)
        # return total_market_cap, top_gainers, top_losers, trading_volume
        return {'Total Market Cap': total_market_cap, 'Top Gainers': top_gainers, 'Top Losers': top_losers, 'Trading Volume': trading_volume}