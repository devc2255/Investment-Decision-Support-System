import streamlit as st
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

@st.cache_resource
def load_sentiment_model():
    """
    Initializes the NLTK VADER sentiment analyzer.
    Ensures the resource downloader runs only once and caches the analyzer object.
    """
    # Securely download the tiny lexicon data file silently
    nltk.download('vader_lexicon', quiet=True)
    return SentimentIntensityAnalyzer()

def analyze_sentiment(headlines):
    if not headlines:
        return {"Bullish": 0.0, "Bearish": 0.0, "Neutral": 100.0, "Overall": "Neutral", "Total_Analyzed": 0}
    
    analyzer = load_sentiment_model()
    
    # Process up to the 15 most recent headlines to keep the UI fast
    target_headlines = headlines[:15]
    
    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
    
    for text in target_headlines:
        # VADER outputs scores for pos, neg, neu, and a compound aggregate
        scores = analyzer.polarity_scores(text)
        compound = scores['compound']
        
        # Map VADER's compound mathematical score to your standard labels
        if compound >= 0.05:
            sentiment_counts["positive"] += 1
        elif compound <= -0.05:
            sentiment_counts["negative"] += 1
        else:
            sentiment_counts["neutral"] += 1
        
    total = len(target_headlines)
    bullish_pct = (sentiment_counts['positive'] / total) * 100
    bearish_pct = (sentiment_counts['negative'] / total) * 100
    neutral_pct = (sentiment_counts['neutral'] / total) * 100
    
    # Maintain your exact logic thresholds for determining overall market sentiment
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
