import os
from langchain_groq import ChatGroq 
from langchain_core.messages import SystemMessage, HumanMessage
from src.agents.state import AgentState

# Initialize LLM
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    temperature=0.2 
)

def analyst_node(state: AgentState):
    """
    The 'Brain' of the operation.
    Reads structured data and writes a draft analysis.
    """
    ticker = state["ticker"]
    prices = state["market_data"]
    techs = state["technicals"]
    news = state["news"]
    
    print(f"--- ANALYST ANALYZING: {ticker} ---")
    
    # 1. Construct the Context 
    context = f"""
    TICKER: {ticker}
    
    --- MARKET DATA & FUNDAMENTALS ---
    Current Price: ${prices.get('current_price', 'N/A')}
    Market Cap: {prices.get('market_cap', 'N/A')}
    P/E Ratio: {prices.get('pe_ratio', 'N/A')}
    Forward P/E: {prices.get('forward_pe', 'N/A')}
    
    Revenue Growth: {prices.get('revenue_growth', 'N/A')}
    Profit Margins: {prices.get('profit_margins', 'N/A')}
    Debt to Equity: {prices.get('debt_to_equity', 'N/A')}
    Free Cash Flow: {prices.get('free_cash_flow', 'N/A')}
    Return on Equity: {prices.get('return_on_equity', 'N/A')}
    
    --- TECHNICAL ANALYSIS ---
    RSI: {techs.get('momentum', {}).get('rsi', {}).get('value', 'N/A')} ({techs.get('momentum', {}).get('rsi', {}).get('signal', 'N/A')})
    MACD: {techs.get('trend', {}).get('macd', {}).get('trend', 'N/A')}
    Overall Signal: {techs.get('overall_signal', {}).get('signal', 'Unknown')}
    Confidence: {techs.get('overall_signal', {}).get('confidence', '0%')}
    
    --- RECENT NEWS & SENTIMENT ---
    """
    

    if isinstance(news, list):
        for i, article in enumerate(news[:5]): 
            title = article.get('title', 'No Title')
            url = article.get('url', 'No URL')
            content = article.get('content', 'No content available')
            context += f"\nArticle {i+1}: {title}\nSource: {url}\nSummary: {content[:400]}...\n"
    else:
        context += f"\nNo specific news data available.\n"

   
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

    human_message = f"Here is the latest data for {ticker}. Write the analysis.\n\nData Context:\n{context}"
    
  
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_message)
    ]
    
    response = llm.invoke(messages)
    
   
    return {
        "analyst_draft": response.content,
        "recommendation": techs.get('overall_signal', {}).get('signal', 'Hold')
    }
