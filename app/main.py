from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.schemas import ChatRequest, ChatResponse
from app.services.rag import initialize_knowledge_base, get_answer_from_rag
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_knowledge_base()
    yield

app = FastAPI(
    title="NusantaraCare RAG API",
    lifespan=lifespan 
)

@app.get("/")
async def root():
    return {"message": "API Aktif. Buka /docs untuk menguji endpoint."}

@app.post("/api/v1/ask", response_model=ChatResponse)
async def ask_assistant(request: ChatRequest):
    hasil = get_answer_from_rag(request.query)
    
    return ChatResponse(
        answer=hasil.get("answer", "Terjadi kesalahan"),
        confidence_label=hasil.get("confidence_label", "low"),
        reason_code=hasil.get("reason_code", "error")
    )