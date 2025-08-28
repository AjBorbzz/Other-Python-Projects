from fastapi import APIRouter

router = APIRouter()

@router.get("", tags=["health"])
async def health():
    return {"status": "ok"}


