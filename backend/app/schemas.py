from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: str
    message: str


class StudyRequest(BaseModel):
    text: str
