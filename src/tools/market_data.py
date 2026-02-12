import yfinance as yf
import pandas as pd
from typing import Dict, Any

def fetch_market_data(ticker: str) -> Dict[str, Any]:
    """
    Fetch comprehensive market data for a given stock ticker.
    Returns a dictionary with summary metrics AND the raw history dataframe.
    """
    try:
        # Clean ticker input
        ticker = ticker.upper().strip()
        stock = yf.Ticker(ticker)
        
        # 1. Fetch Info (Metadata & Fundamentals)
        try:
            info = stock.info
        except:
            info = {}

        # 2. Fetch History (Needed for Volatility & Technicals)
        hist = stock.history(period="6mo")
        
        if hist.empty:
            return {"error": f"No price data available for ticker: {ticker}"}
            
        # 3. Calculate Derived Metrics
        current_price = hist['Close'].iloc[-1]
        
        # Volatility (30-day rolling std dev of percent change)
        if len(hist) >= 30:
            volatility = hist['Close'].pct_change().rolling(window=30).std().iloc[-1] * 100
        else:
            volatility = 0.0
        
        # 4. Construct the Payload (Now with DEEP Fundamental Data)
        market_data = {
            "ticker": ticker,
            "current_price": round(current_price, 2),
            "volatility_30d": round(volatility, 2) if pd.notnull(volatility) else "N/A",
            
            # --- NEW FUNDAMENTAL METRICS ---
            "market_cap": info.get('marketCap', 'N/A'),
            "pe_ratio": info.get('trailingPE', 'N/A'),
            "forward_pe": info.get('forwardPE', 'N/A'),
            "revenue_growth": info.get('revenueGrowth', 'N/A'),
            "profit_margins": info.get('profitMargins', 'N/A'),
            "debt_to_equity": info.get('debtToEquity', 'N/A'),
            "free_cash_flow": info.get('freeCashflow', 'N/A'),
            "return_on_equity": info.get('returnOnEquity', 'N/A'),
            
            # HIDDEN FIELD: The raw dataframe for the Technical Analysis Node
            "history_df": hist 
        }
        
        return market_data

    except Exception as e:
        return {"error": f"Market data fetch failed: {str(e)}"}