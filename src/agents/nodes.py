from src.agents.state import AgentState
from src.tools.market_data import fetch_market_data
from src.tools.technicals import calculate_technicals
from src.tools.news import get_market_news


def market_data_node(state: AgentState):
    """
    1. Fetches market data (Price, Volume, Peers).
    2. Updates the state with 'market_data' (for the LLM).
    3. Stores the raw 'price_history' DataFrame (for the Technical Analysis node).
    """
    ticker = state["ticker"]
    
    # 1. Run the Tool
    result = fetch_market_data(ticker)
    
    # 2. Check for Errors
    if "error" in result:
        return {"errors": [result["error"]]}
        
    # 3. Extract the DataFrame (The LLM doesn't see this yet)
    # We use .pop() to remove it from the dictionary so the LLM gets clean JSON
    history_df = result.pop("history_df", None)
    
    # 4. Return Updates to State
    return {
        "market_data": result,       # The clean dictionary (Price, P/E, etc.)
        "price_history": history_df  # The raw DataFrame for the next node
    }

def technical_analysis_node(state: AgentState):
    """
    1. Reads the 'price_history' dataframe from the state.
    2. Calculates technical indicators (RSI, MACD, etc.).
    3. Updates 'technicals' in the state.
    """
    # 1. Get the dataframe we saved earlier
    history_df = state.get("price_history")
    
    # Safety Check: Did the previous node fail or return empty data?
    if history_df is None or history_df.empty:
        return {"errors": ["No price history found for technical analysis"]}

    print(f"--- ANALYZING TECHNICALS FOR: {state['ticker']} ---")

    # 2. Run the Tool
    tech_metrics = calculate_technicals(history_df)
    
    if "error" in tech_metrics:
        return {"errors": [tech_metrics["error"]]}

    # 3. Return Updates
    return {
        "technicals": tech_metrics
    }


def news_gatherer_node(state: AgentState):
    """
    1. Searches for news based on the ticker.
    2. Updates the 'news' list in the state.
    """
    ticker = state["ticker"]
    
    # Enhanced query for better results
    query = f"{ticker} stock news analysis market trends"
    
    # Run the tool
    news_items = get_market_news(query)
    
    # Check for errors
    if news_items and "error" in news_items[0]:
         return {"errors": [news_items[0]['error']]}

    return {
        "news": news_items
    }

# src/agents/nodes.py

def analyst_node(state: AgentState):
    # ... (existing code getting ticker, prices, etc.) ...
    
    # ---------------- PASTE THE NEW PROMPT HERE ----------------
    system_prompt = """You are a veteran Hedge Fund Portfolio Manager with 20 years of experience. 
    Your job is to produce a high-conviction investment memorandum.

    ### INSTRUCTIONS:
    1. **BE DECISIVE:** You must output a distinct signal: BUY, SELL, or HOLD. A "Hold" with low confidence is a failure.
    2. **USE THE DATA:** You have been provided with specific financial metrics (P/E, Margins, Debt). Cite them in your analysis.
    3. **CITE SOURCES:** You have news articles with URLs. Explicitly reference them (e.g., "According to Reuters [Source 1]...").
    4. **NO EXCUSES:** Never say "I lack data." If a metric is missing, make a reasonable inference based on the sector and price action.
    5. **CONFIDENCE SCORE:** You must provide a confidence score (0-100%). Scores below 50% are unacceptable; dig deeper to form a view.

    ### FORMAT:
    Structure your response as a professional Wall Street Memo:
    1. **Executive Summary:** The Call (Buy/Sell) and the Target Price rationale.
    2. **Fundamental Deep Dive:** Analysis of Valuation (P/E), Growth, and Balance Sheet health.
    3. **Technical Analysis:** Price action, RSI, and MACD trends.
    4. **Sentiment & News:** Summary of key headlines and their potential impact.
    5. **Risks:** The bear case (e.g., high debt, falling margins).
    
    Tone: Professional, objective, and data-driven."""
    # ---------------- END PASTE ----------------

    # ... (rest of the code calling the LLM) ...