from pydantic import BaseModel
from typing import List

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str
    is_crisis: bool

class MessageHistory(BaseModel):
    role: str
    content: str

    class Config:
        orm_mode = True