from fastapi import APIRouter, HTTPException, Depends 
from app.models.schemas import SummarizeRequest, SummarizeResponse
from app.services.llm import chat_complete
from app.core.deps import get_current_user 


router = APIRouter()

SYSTEM_PROMPT = (
    "You are a SOC assistant. Summarize SIEM logs into a concise , actionable report with "
    "key findings, entities, anomalies, and next steps. Be precise and avoid hallucinations. If unsure, you can always say so"
)

@router.post("", response_model=SummarizeResponse, tags=["summarize"])
async def summarize(req: SummarizeRequest, user=Depends(get_current_user)):
    if not req.logs:
        raise HTTPException(status_code=400, detail="logs[] cannot be empty")
    joined = "\n".join(req.logs)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"incident {req.incident_id}\nlogs:\n:{joined}"}
    ]

    try:
        content = await chat_complete(messages)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
    
    return SummarizeResponse(incident_id=req.incident_id, summary=content, model="llama3")