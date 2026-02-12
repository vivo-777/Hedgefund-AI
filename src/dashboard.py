import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# --- IMPORT THE AGENT DIRECTLY (No more API calls) ---
# We try to import 'app' from src.main. If your file is named differently, adjust this.
try:
    from src.main import app
except ImportError:
    # Fallback for local testing if paths are messy
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.main import app

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="AI Hedge Fund", layout="wide")
st.title("🤖 AI Hedge Fund (Monolith)")

# --- 2. SIDEBAR ---
with st.sidebar:
    st.header("Trade Settings")
    ticker = st.text_input("Ticker Symbol", value="NVDA").upper()
    max_revisions = st.number_input("Max Risk Revisions", min_value=1, max_value=5, value=2)
    run_btn = st.button("Generate Analysis", type="primary")

# --- 3. MAIN LOGIC ---
if run_btn:
    with st.spinner(f"Running autonomous agents for {ticker}..."):
        try:
            # --- THE FIX: DIRECT INVOCATION ---
            # Instead of requests.post(...), we call the Python function directly.
            initial_state = {
                "ticker": ticker, 
                "max_revisions": max_revisions,
                "revision_count": 0
            }
            
            # This runs the entire LangGraph workflow in memory
            final_state = app.invoke(initial_state)
            
            # --- 4. PARSE DATA (From State Dict) ---
            # The structure of 'final_state' matches your agent's state definition
            market_data = final_state.get("market_data", {})
            technicals = final_state.get("technicals", {})
            news = final_state.get("news", [])
            analyst_draft = final_state.get("analyst_draft", "No report generated.")
            critique = final_state.get("critique")
            
            # --- 5. DISPLAY RESULTS ---
            
            # Top Metrics Row
            col1, col2, col3 = st.columns(3)
            current_price = market_data.get("current_price", "N/A")
            
            col1.metric("Ticker", ticker)
            col2.metric("Current Price", f"${current_price}")
            
            # Show the signal if available, otherwise just "Generated"
            signal = technicals.get('overall_signal', {}).get('signal', 'Generated')
            col3.metric("Analyst Decision", signal)

            # Tabs for details
            tab1, tab2, tab3 = st.tabs(["📝 Research Report", "📊 Market Data", "🧠 Agent Logic"])
            
            with tab1:
                st.markdown("### Investment Memo")
                st.markdown(analyst_draft)
            
            with tab2:
                st.subheader("Recent News")
                if news:
                    for article in news[:5]: # Show top 5
                        title = article.get('title', 'No Title')
                        url = article.get('url', '#')
                        st.markdown(f"- **{title}** [Read Source]({url})")
                else:
                    st.info("No news data returned.")
                
                st.divider()
                st.subheader("Raw Financials")
                st.json(market_data)
                    
            with tab3:
                st.subheader("Risk Management Critique")
                if critique:
                    st.warning(f"Risk Manager Feedback:\n\n{critique}")
                else:
                    st.success("Risk Manager approved the report immediately.")
                    
                st.subheader("Technical Indicators")
                st.json(technicals)

        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
            st.markdown("Check the logs in Render for more details.")
