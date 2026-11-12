from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

from app import storage

router = APIRouter()


class ChatRequest(BaseModel):
    session_id: str
    message: str


class StudyRequest(BaseModel):
    text: str


@router.post("/chat")
def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="消息不能为空")
    storage.add_message(request.session_id, "user", request.message)

    # 模拟回复，不依赖真实API
    reply = f"这是模拟回复：我收到了你的消息 '{request.message}'"
    storage.add_message(request.session_id, "assistant", reply)
    return {"session_id": request.session_id, "reply": reply}


@router.post("/chat/stream")
def chat_stream(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="消息不能为空")
    storage.add_message(request.session_id, "user", request.message)

    def generate():
        fake_chunks = ["这是", "一个", "流式", "输出", "的", "测试。"]
        full_reply = "".join(fake_chunks)
        yield full_reply
        storage.add_message(request.session_id, "assistant", full_reply)

    return StreamingResponse(generate(), media_type="text/plain")


@router.get("/sessions")
def list_sessions():
    return {"sessions": storage.get_all_sessions()}


@router.get("/sessions/{session_id}/messages")
def get_messages(session_id: str):
    history = storage.get_history(session_id)
    if not history:
        raise HTTPException(status_code=404, detail="找不到该会话")
    return {"session_id": session_id, "messages": history}


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    if session_id not in storage.get_all_sessions():
        raise HTTPException(status_code=404, detail="找不到该会话")
    storage.clear_history(session_id)
    return {"message": "会话已清空"}


@router.post("/study/correct")
def study_correct(request: StudyRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="不能为空")
    reply = f"【语法解析】原句：{request.text}。建议修改为更地道的表达。"
    return {"original": request.text, "correction": reply}
