from pydantic import BaseModel, Field
from typing import Literal

class ChatRequest(BaseModel):
    query: str = Field(..., description="Pertanyaan dari pengguna", example="Berapa lama SLA tiket P2?")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="Jawaban final sistem RAG")
    confidence_label: Literal["high", "medium", "low"] = Field(..., description="Tingkat keyakinan jawaban")
    reason_code: str = Field(..., description="Alasan sistem memberikan jawaban tersebut (contoh: answered, no_relevant_context, out_of_scope)")
