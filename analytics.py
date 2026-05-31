import os
import requests
import streamlit as st
from datetime import datetime, timedelta

class FinnhubClient:
    def __init__(self):
        self.api_key = os.environ.get("FINNHUB_API_KEY")
        self.base_url = "https://finnhub.io/api/v1"

    def is_configured(self):
        return bool(self.api_key)

    def set_api_key(self, key):
        self.api_key = key

    def get_company_profile(self, ticker):
        url = f"{self.base_url}/stock/profile2"
        params = {"symbol": ticker.upper(), "token": self.api_key}
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                return {"error": "Rate limit exceeded. Try again in a minute."}
            return {"error": f"API error {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Connection failed: {str(e)}"}

    def get_financial_metrics(self, ticker):
        url = f"{self.base_url}/stock/metric"
        params = {"symbol": ticker.upper(), "metric": "all", "token": self.api_key}
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json().get("metric", {})
            return {}
        except requests.exceptions.RequestException:
            return {}

    def search_symbol(self, query):
        url = f"{self.base_url}/search"
        params = {"q": query, "token": self.api_key}
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json().get("result", [])
            return []
        except requests.exceptions.RequestException:
            return []

    def get_company_news(self, ticker, days=7):
        """Fetches recent company news from Finnhub."""
        url = f"{self.base_url}/company-news"
        to_date = datetime.now().strftime('%Y-%m-%d')
        from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        params = {"symbol": ticker.upper(), "from": from_date, "to": to_date, "token": self.api_key}
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            return []
        except requests.exceptions.RequestException:
            return []
