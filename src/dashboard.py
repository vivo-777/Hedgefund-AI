import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go # type: ignore
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="AI Hedge Fund", layout="wide")
st.title("🤖 AI Hedge Fund (Microservices)")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# --- 2. SIDEBAR ---
with st.sidebar:
    st.header("Trade Settings")
    ticker = st.text_input("Ticker Symbol", value="NVDA").upper()
    max_revisions = st.number_input("Max Risk Revisions", min_value=1, max_value=5, value=2)
    run_btn = st.button("Generate Analysis", type="primary")

# --- 3. MAIN LOGIC ---
if run_btn:
    with st.spinner(f"Contacting Analyst Agent for {ticker}..."):
        try:
            # A. Prepare the Payload
            payload = {
                "ticker": ticker,
                "max_revisions": max_revisions
            }
            
            # B. Call the API 
   
            response = requests.post(f"{BACKEND_URL}/analyze", json=payload, timeout=120)
            
            # C. Check for Server Errors (500, 404, etc.)
            response.raise_for_status()
            
            # D. Parse the Data
            data = response.json()
            
            # --- 4. DISPLAY RESULTS ---
            
            # Top Metrics Row
            col1, col2, col3 = st.columns(3)
            current_price = data.get("current_price", "N/A")
            

            # If 'market_cap' is missing in API response, we handle it gracefully.
            col1.metric("Ticker", data.get("ticker"))
            col2.metric("Current Price", f"${current_price}")
            col3.metric("Analyst Decision", "Generated")

            # Tabs for details
            tab1, tab2, tab3 = st.tabs(["📝 Research Report", "📊 Market Data", "🧠 Agent Logic"])
            
            with tab1:
                st.markdown("### Investment Memo")
                st.markdown(data.get("analyst_draft", "No report generated."))
            
            with tab2:
                st.subheader("Recent News")
                news_items = data.get("news", [])
                if news_items:
                    for article in news_items:
                        st.markdown(f"- **{article.get('title')}** [Read Source]({article.get('url')})")
                else:
                    st.info("No news data returned.")
                    
            with tab3:
                st.subheader("Risk Management Critique")
                critique = data.get("critique")
                if critique:
                    st.warning(f"Risk Manager Feedback:\n\n{critique}")
                else:
                    st.success("Risk Manager approved the report immediately.")
                    
                st.subheader("Technical Indicators")
                st.json(data.get("technicals", {}))

        except requests.exceptions.ConnectionError:
            st.error(f"🚨 Connection Refused: Could not connect to {BACKEND_URL}.")
            st.markdown("Is the **Backend API** running? Try running `uvicorn src.api:api --reload` in a separate terminal.")
            
        except requests.exceptions.Timeout:
            st.error("🚨 Timeout: The analysis took too long. The agent might be stuck in a loop.")
            
        except requests.exceptions.HTTPError as err:
            st.error(f"🚨 API Error ({err.response.status_code}): {err.response.text}")
            
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")