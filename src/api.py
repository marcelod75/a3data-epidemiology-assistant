# src/api.py
from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
from dotenv import load_dotenv
import os

# importa o agente RAG
from src.rag_agent import RagAgent  # type: ignore

# carrega .env a partir da raiz do projeto
ROOT = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=str(ROOT / ".env"), override=True)

app = FastAPI(title="A3Data Epidemiology Assistant API")
agent = RagAgent()

class AskReq(BaseModel):
    question: str
    k: int = 5

@app.post("/ask")
def ask(req: AskReq):
    return agent.ask(req.question, k=req.k)
