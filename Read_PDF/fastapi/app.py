from fastapi import FastAPI
# from modules import extract_pdf
from pydantic import BaseModel

class UserInput(BaseModel):
    inpt_pdf : str

app = FastAPI()

@app.get("/")
async def root():
    return {"Hey Aj": "It's time for your coffee break!"}