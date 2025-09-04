from typing import Optional, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field 
import httpx
import asyncio 


OLLAMA_URL = "http://localhost:11434/api/generate"

app = FastAPI(title="SIEM Log Summarizer (LLama3 POC)", version="0.1.0")

class SummarizeRequest(BaseModel):
    log: str = Field(..., description="RAW SIEM Log line or multi-line blob")
    model: str = Field(default="llama3:8b", description="Ollama model blob")
    max_tokens: int = Field(default=256, ge=32, le=2048)
    temperature: float = Field(default=0.2, ge=0.0, le=1.0)
    suspected_threat: Optional[str] = None
    known_iocs: Optional[List[str]] = None 


class SummarizeResponse(BaseModel):
    model: str
    summary: str
    tokens_used: Optional[int] = None

SYSTEM_INSTRUCTIONS = """You are an expert SOC analyst.
Summarize the following SIEM raw log(s) for a level-2 SOC handoff.
Be concise and structured.

Return:
- Brief summary (1–2 sentences)
- Entities/IOCs (IPs, users, hosts)
- Likely tactic/technique (MITRE if obvious)
- Severity (Low/Med/High) + rationale
- Next steps (2–4 bullets)
Avoid speculation; flag uncertainty clearly.
"""

USER_TEMPLATE = """SIEM RAW LOG(S):
{log}

Context:
- Suspected threat: {suspected_threat}
- Known IOCs: {known_iocs}
"""

async def call_ollama(model:str, prompt: str, max_tokens: int, temperature: float) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": temperature
        }
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(OLLAMA_URL, json=payload)
        r.raise_for_status()
        data = r.json()
        return data.get("response", "").strip()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Ollama call failed: {e}")
    
@app.get("/health")
async def health():
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            await client.get("http://localhost:11434/")
        return {"status": "ok", "ollama": "reachable"}
    except Exception:
        return {"status": "ok","ollama":"unreachable (start ollama if using local llama 3)"}
    
@app.post("/summarize", response_model=SummarizeResponse)
async def summarize(req: SummarizeRequest):
    user_block = USER_TEMPLATE.format(
        log=req.log.strip(),
        suspected_threat=req.suspected_threat or "n/a",
        known_iocs=", ".join(req.known_iocs) if req.known_iocs else "n/a"
    )
    full_prompt = f"<<SYS>>\n{SYSTEM_INSTRUCTIONS}\n<</SYS>>\n\n{user_block}"
    summary = await call_ollama(
        model=req.model,
        prompt=full_prompt,
        max_tokens=req.max_tokens,
        temperature=req.temperature
    )
    return SummarizeResponse(model=req.model, summary=summary, tokens_used=None)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)