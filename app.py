# app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import storage
from llm import build_client, chat_once
from config import get_settings

app = FastAPI(title="聊天机器人接口")

# 1. 定义接收消息的格式（对应作业要求的 {"session_id":"u1", "message":"你好"}）
class ChatRequest(BaseModel):
    session_id: str
    message: str

# 2. 普通对话接口 POST /chat
@app.post("/chat")
def chat(request: ChatRequest):
    # 空消息校验
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="消息不能为空")
    
    session_id = request.session_id
    
    # 取出之前的聊天记录
    history = storage.get_history(session_id)
    # 把用户这次说的话加进去
    storage.add_message(session_id, "user", request.message)
    
    # 调用上次写好的大模型函数
    
        # 如果没配真实的 Key，这里为了测试能跑通，我们给个模拟回复
    reply = f"这是模拟回复：我收到了你的消息 '{request.message}'"
        
    # 把大模型的回复也存进历史记录
    storage.add_message(session_id, "assistant", reply)
    
    # 返回要求的格式
    return {"session_id": session_id, "reply": reply}

# 3. 查看所有会话列表 GET /sessions
@app.get("/sessions")
def list_sessions():
    return {"sessions": storage.get_all_sessions()}

# 4. 查看某个会话的消息记录 GET /sessions/{session_id}/messages
@app.get("/sessions/{session_id}/messages")
def get_messages(session_id: str):
    history = storage.get_history(session_id)
    if not history:
        raise HTTPException(status_code=404, detail="找不到该会话")
    return {"session_id": session_id, "messages": history}

# 5. 清空某个会话 DELETE /sessions/{session_id}
@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    if session_id not in storage.get_all_sessions():
        raise HTTPException(status_code=404, detail="找不到该会话")
    storage.clear_history(session_id)
    return {"message": "会话已清空"}
from fastapi.responses import StreamingResponse

# 6. 流式输出接口 POST /chat/stream
@app.post("/chat/stream")
def chat_stream(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="消息不能为空")
    
    session_id = request.session_id
    history = storage.get_history(session_id)
    storage.add_message(session_id, "user", request.message)
    
    def generate():
        full_reply = ""
        try:
            # 假装调用大模型的流式接口
            fake_chunks = ["这是", "一个", "流式", "输出", "的", "测试。"]
            for chunk in fake_chunks:
                full_reply += chunk
                yield chunk
        except Exception:
            err_msg = "连接模型失败"
            full_reply += err_msg
            yield err_msg
            
        storage.add_message(session_id, "assistant", full_reply)
        
    return StreamingResponse(generate(), media_type="text/plain")


# 7. 学习功能：英语纠错 (POST /study/correct)
class StudyRequest(BaseModel):
    text: str

@app.post("/study/correct")
def study_correct(request: StudyRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="不能为空")
        
    reply = f"【语法解析】原句：{request.text}。建议修改为更地道的表达。"
    return {"original": request.text, "correction": reply}