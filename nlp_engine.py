import streamlit as st
from transformers import pipeline

@st.cache_resource
def load_sentiment_model():
    """
    Loads the FinBERT model. 
    @st.cache_resource ensures the model is kept in memory across UI reloads.
    """
    return pipeline("sentiment-analysis", model="ProsusAI/finbert")

def analyze_sentiment(headlines):
    if not headlines:
        return {"Bullish": 0.0, "Bearish": 0.0, "Neutral": 100.0, "Overall": "Neutral", "Total_Analyzed": 0}
    
    analyzer = load_sentiment_model()
    
    # Process up to the 15 most recent headlines to keep the UI fast
    results = analyzer(headlines[:15])
    
    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
    for res in results:
        label = res['label'].lower()
        sentiment_counts[label] += 1
        
    total = len(results)
    bullish_pct = (sentiment_counts['positive'] / total) * 100
    bearish_pct = (sentiment_counts['negative'] / total) * 100
    neutral_pct = (sentiment_counts['neutral'] / total) * 100
    
    overall = "Neutral"
    if bullish_pct > bearish_pct and bullish_pct >= 40:
        overall = "Bullish"
    elif bearish_pct > bullish_pct and bearish_pct >= 40:
        overall = "Bearish"
        
    return {
        "Bullish": bullish_pct,
        "Bearish": bearish_pct,
        "Neutral": neutral_pct,
        "Overall": overall,
        "Total_Analyzed": total
    }
