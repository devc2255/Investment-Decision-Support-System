# Investment Decision Support System

A Streamlit-based capital origination and deal pipeline tracker for M&A and private equity deal flow.

## Features

- Add and manage deal origination entries with ticker, target name, sector, market cap, thesis, and status.
- Persist deal records in a local SQLite database (`deals_pipeline.db`).
- Search and autofill company profile data using the Finnhub API.
- Live sentiment analysis of recent company news using NLTK VADER.
- Executive dashboard views with portfolio KPIs and interactive charts.

## Repository Structure

- `app.py` - Streamlit app UI and workflow.
- `analytics.py` - Finnhub API client for company profile, financial metrics, symbol search, and news.
- `database.py` - SQLite database helpers for the deal ledger.
- `nlp_engine.py` - Sentiment analysis utilities powered by NLTK VADER.
- `requirements.txt` - Python dependencies.

## Requirements

- Python 3.10+
- Streamlit
- pandas
- requests
- plotly
- nltk

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set your Finnhub API key. You can add it to Streamlit secrets or provide it at runtime by entering it into the app.

Example `.streamlit/secrets.toml`:

```toml
[general]
FINNHUB_API_KEY = "your_finnhub_api_key"
```

## Run the App Locally through VScode Terminal

```bash
streamlit run app.py
```

## Live Demo
Streamlit Community Online Deployed - `https://investment-decision-support-system-h7pderxebhpp4zcd8quhed.streamlit.app/`.

- Use the sidebar to configure your Finnhub API key, search or enter a ticker, and autofill company details.
- Add deals to the pipeline and monitor them in the Active Ledger.
- Switch to the AI Analyst tab for sentiment analysis and to the Executive Summary tab for portfolio KPIs and charts.

## Usage

- Use the sidebar to enter a ticker or search for a company by name.
- Autofill company metadata from Finnhub and add deals to the ledger.
- View the active deal ledger, run AI analyst screening, and explore executive summary charts.

## Notes

- The local SQLite database file is ignored by `.gitignore`.
- News sentiment analysis is limited to the most recent headlines returned by Finnhub.
- If the Finnhub API key is not configured, the app will request it in-session.
