import streamlit as st
import database as db
import pandas as pd
import re
import plotly.express as px
from analytics import FinnhubClient
from nlp_engine import analyze_sentiment

# Initialize database and Finnhub client
db.init_db()
finnhub = FinnhubClient()

st.set_page_config(page_title="Capital Origination Pipeline", page_icon="📈", layout="wide")

# --- Header & API Management ---
st.title("📈 Capital Origination & Deal Pipeline")
st.markdown("Enterprise-grade M&A and Private Equity Deal Tracking System")

if not finnhub.is_configured():
    with st.expander("🔑 Configure Finnhub API Key", expanded=True):
        user_key = st.text_input("Enter Finnhub API Token:", type="password")
        if user_key:
            finnhub.set_api_key(user_key)
            st.success("API key applied for this session!")
            st.rerun()

# --- Callback Function for Deletion ---
def handle_delete(deal_id):
    db.delete_deal(deal_id)
    st.toast("Deal successfully removed from pipeline!", icon="🗑️")

# --- Initialize Session State ---
if "autofill_name" not in st.session_state: st.session_state.autofill_name = ""
if "autofill_sector" not in st.session_state: st.session_state.autofill_sector = "Technology"
if "autofill_mcap" not in st.session_state: st.session_state.autofill_mcap = 0.0

# ==========================================
# SIDEBAR: DEAL ORIGINATION
# ==========================================
st.sidebar.header("Originate Deal")

with st.sidebar.expander("❓ Don't know the Ticker? Search here"):
    search_query = st.text_input("Company Name", key="company_lookup")
    if st.button("Lookup Symbol"):
        if search_query:
            with st.spinner("Searching..."):
                results = finnhub.search_symbol(search_query)
                if results:
                    stocks = [r for r in results if r.get("type") == "Common Stock"]
                    display_results = stocks[:5] if stocks else results[:5]
                    for res in display_results:
                        st.markdown(f"**{res['symbol']}** — {res['description']}")
                else:
                    st.info("No matching public stocks found.")

ticker_input = st.sidebar.text_input("Ticker Symbol (e.g., AAPL)", key="sidebar_ticker").upper()

if st.sidebar.button("🔍 Autofill via Finnhub"):
    if ticker_input and finnhub.is_configured():
        with st.spinner("Fetching company details..."):
            profile = finnhub.get_company_profile(ticker_input)
            if profile and "error" not in profile:
                st.session_state.autofill_name = profile.get("name", "")
                st.session_state.autofill_sector = profile.get("finnhubIndustry", "Other")
                st.session_state.autofill_mcap = float(profile.get("marketCapitalization", 0.0))
                st.sidebar.success("Data fetched!")
            else:
                st.sidebar.error("Could not find data.")

st.sidebar.markdown("---")
target_name = st.sidebar.text_input("Target Entity Name", value=st.session_state.autofill_name)
sector_options = ["Technology", "Healthcare", "Financials", "Industrials", "Consumer Discretionary", "Other"]
default_sector_idx = sector_options.index(st.session_state.autofill_sector) if st.session_state.autofill_sector in sector_options else 5

sector = st.sidebar.selectbox("Sector", sector_options, index=default_sector_idx)
market_cap = st.sidebar.number_input("Est. Market Cap ($M)", min_value=0.0, step=10.0, value=st.session_state.autofill_mcap)
thesis = st.sidebar.text_area("Investment Thesis")
status = st.sidebar.selectbox("Pipeline Status", ["Sourced", "Initial Screening", "Due Diligence", "Term Sheet", "Closed", "Passed"])

if st.sidebar.button("💾 Add to Ledger", type="primary", use_container_width=True):
    if ticker_input and target_name:
        db.add_deal(ticker_input, target_name, sector, market_cap, thesis, status)
        st.session_state.autofill_name = ""
        st.session_state.autofill_mcap = 0.0
        st.rerun()

# MAIN DASHBOARD: EXECUTIVE TABS
# ==========================================
deals_df = db.get_all_deals()

if not deals_df.empty:
    deals_df["Visual ID"] = range(1, len(deals_df) + 1)
    
    # Reordered Tabs: Ledger -> AI Analyst -> Executive Summary
    tab1, tab2, tab3 = st.tabs(["📋 Active Ledger", "🧠 AI Analyst & Management", "📊 Executive Summary"])
    
    # --- TAB 1: ACTIVE LEDGER (Now First) ---
    with tab1:
        st.subheader("Master Deal Ledger")
        st.dataframe(
            deals_df,
            column_config={
                "id": None, 
                "Visual ID": "ID", 
                "market_cap": st.column_config.NumberColumn("Market Cap ($M)", format="$%d"),
                "entry_date": st.column_config.DateColumn("Origination Date")
            },
            width="stretch",
            hide_index=True,
            column_order=["Visual ID", "ticker", "target_name", "sector", "market_cap", "thesis", "status", "entry_date"] 
        )

    # --- TAB 2: AI ANALYST & PIPELINE MANAGEMENT (Now Second) ---
    with tab2:
        manage_col, analyze_col = st.columns([1, 2])
        
        with manage_col:
            st.subheader("Target Selection")
            deal_options = deals_df.apply(
                lambda row: f"{row['Visual ID']}: [{row['id']}] - {row['ticker']} ({row['target_name']})", 
                axis=1
            ).tolist()
            
            selected_deal_str = st.selectbox("Select Target for Analysis or Deletion", deal_options)
            
            db_id_match = re.search(r'\[(\d+)\]', selected_deal_str)
            if db_id_match:
                selected_id = int(db_id_match.group(1))
                selected_ticker = selected_deal_str.split("] - ")[1].split(" ")[0]
                
                st.markdown("---")
                st.button(
                    "Delete Deal from Pipeline", 
                    type="primary", 
                    key=f"delete_btn_{selected_id}", 
                    on_click=handle_delete, 
                    args=(selected_id,)
                )
            
        with analyze_col:
            st.subheader("💡 Live Analyst Screening")
            if finnhub.is_configured() and db_id_match:
                with st.spinner(f"Fetching structural data for {selected_ticker}..."):
                    profile = finnhub.get_company_profile(selected_ticker)
                    metrics = finnhub.get_financial_metrics(selected_ticker)
                    
                if profile and "error" not in profile:
                    st.markdown(f"#### {profile.get('name', selected_ticker)} ({profile.get('finnhubIndustry', 'N/A')})")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Live Market Cap", f"${profile.get('marketCapitalization', 0):,.1f}M")
                    pe_ttm = metrics.get("peTTM", "N/A")
                    # Check for both standard string "N/A" and Python's None type
                    m2.metric("P/E Ratio (TTM)", f"{pe_ttm:.2f}x" if isinstance(pe_ttm, (int, float)) else "N/A")
                    debt_equity = metrics.get("debtEquityTotalTTM", metrics.get("debtEquityttm", "N/A"))
                    m3.metric("Debt / Equity", f"{debt_equity:.2f}%" if debt_equity not in ["N/A", None] else "N/A")

                    st.markdown("---")
                    st.markdown("##### 🧠 AI Market Sentiment Analysis")
                    
                    with st.spinner("Evaluating NLP sentiment model..."):
                        recent_news = finnhub.get_company_news(selected_ticker, days=7)
                        if recent_news:
                            headlines = [article.get('headline') for article in recent_news if article.get('headline')]
                            if headlines:
                                sentiment = analyze_sentiment(headlines)
                                s1, s2, s3 = st.columns(3)
                                stance_color = "green" if sentiment['Overall'] == "Bullish" else "red" if sentiment['Overall'] == "Bearish" else "gray"
                                s1.markdown(f"**Consensus:** <span style='color:{stance_color}; font-weight:bold;'>{sentiment['Overall']}</span>", unsafe_allow_html=True)
                                s2.metric("Bullish Signal", f"{sentiment['Bullish']:.1f}%")
                                s3.metric("Bearish Signal", f"{sentiment['Bearish']:.1f}%")
                                
                                with st.expander(f"View Data Sources ({sentiment['Total_Analyzed']} Articles)"):
                                    for article in recent_news[:5]:
                                        st.markdown(f"- **{article.get('headline')}** *(Source: {article.get('source')})*")
                            else:
                                st.info("No actionable headlines found in recent news data.")
                        else:
                            st.info("No recent news found for this entity.")

    # --- TAB 3: EXECUTIVE SUMMARY (Now Third) ---
    with tab3:
        st.subheader("Portfolio Overview")
        
        # Top-level KPIs
        kpi1, kpi2, kpi3 = st.columns(3)
        total_value = deals_df['market_cap'].sum()
        avg_value = deals_df['market_cap'].mean()
        
        # --- Dynamic Number Formatter ---
        def format_valuation(mcap_in_millions):
            if mcap_in_millions >= 1_000_000:
                # Trillions
                return f"${mcap_in_millions / 1_000_000:,.2f}T"
            elif mcap_in_millions >= 1_000:
                # Billions
                return f"${mcap_in_millions / 1_000:,.2f}B"
            else:
                # Millions
                return f"${mcap_in_millions:,.1f}M"
        
        kpi1.metric("Active Deals Sourced", len(deals_df))
        kpi2.metric("Total Pipeline Value", format_valuation(total_value))
        kpi3.metric("Avg. Target Market Cap", format_valuation(avg_value))
        
        st.markdown("---")
        
        # Interactive Visualizations
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            fig_sector = px.pie(deals_df, names='sector', title="Pipeline Exposure by Sector", hole=0.4)
            fig_sector.update_layout(margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig_sector, use_container_width=True)
            
        with chart_col2:
            status_counts = deals_df['status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            fig_status = px.bar(status_counts, x='Status', y='Count', title="Deals by Funnel Stage", color='Status')
            fig_status.update_layout(showlegend=False, margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig_status, use_container_width=True)

else:
    st.info("Your pipeline is currently empty. Use the sidebar to originate a new deal.")