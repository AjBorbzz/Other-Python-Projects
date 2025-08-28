from fastapi import APIRouter, HTTPException, Depends 
from app.models.schemas import SummarizeRequest, SummarizeResponse
from app.services.llm import chat_complete
from app.core.deps import get_current_user 
from app.services.providers import get_chat_client
from app.core.config import Settings


router = APIRouter()

SYSTEM_PROMPT = (
    "You are a SOC assistant. Summarize SIEM logs into a concise , actionable report with "
    "key findings, entities, anomalies, and next steps. Be precise and avoid hallucinations. If unsure, you can always say so"
)

@router.post("", response_model=SummarizeResponse, tags=["summarize"])
async def summarize(req: SummarizeRequest, user=Depends(get_current_user)):
    if not req.logs:
        raise HTTPException(status_code=400, detail="logs[] cannot be empty")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Incident: {req.incident_id}\nLogs:\n" + "\n".join(req.logs)},
    ]

    chat = get_chat_client(req.provider)
    content = await chat(messages)

    provider = (req.provider or Settings.DEFAULT_PROVIDER)
    model = Settings.OPENAI_MODEL if provider == "openai" else Settings.LLM_MODEL
    return SummarizeResponse(incident_id=req.incident_id, summary=content, provider=provider, model=model)
