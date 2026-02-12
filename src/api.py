
from fastapi import FastAPI, HTTPException 
from pydantic import BaseModel
from src.main import app as graph_app  
import uvicorn # type: ignore

class AnalysisRequest(BaseModel):
    ticker: str
    max_revisions: int = 2

api = FastAPI(title="Hedge Fund Agent API", version="1.0")

@api.get("/")
def health_check():
    return {"status": "active", "model": "Llama-3.3-70b"}

@api.post("/analyze")
async def run_analysis(request: AnalysisRequest):
    """
    Triggers the LangGraph workflow for a specific ticker.
    """
    try:
        initial_state = {
            "ticker": request.ticker,
            "max_revisions": request.max_revisions,
            "revision_number": 0,
            "market_data": {},
            "technicals": {},
            "news": [],
            "analyst_draft": "",
            "critique": "",
            "final_report": "",
            "errors": []
        }
        
        result = await graph_app.ainvoke(initial_state)

        return {
            "ticker": result["ticker"],
            "market_data": result["market_data"],
            "analyst_draft": result["analyst_draft"],
            "critique": result["critique"],
            "news": result["news"][:3],
            "technicals": result["technicals"],
            "price_history": result["price_history"].reset_index().to_dict(orient='records') if result["price_history"] is not None else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("src.api:api", host="0.0.0.0", port=8000, reload=True)
