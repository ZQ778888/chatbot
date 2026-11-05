# storage.py
# 这个文件用来在内存里存聊天记录，以后学了数据库，把这个换掉就行

# 用一个字典来存所有人的聊天记录
# 结构大概是： {"用户1的id": [{"role": "user", "content": "你好"}], "用户2的id": [...]}
_chat_history = {}

def get_history(session_id: str) -> list:
    """获取某个用户的聊天记录，如果没有就返回空列表"""
    return _chat_history.get(session_id, [])

def add_message(session_id: str, role: str, content: str):
    """往某个用户的记录里加一条消息"""
    if session_id not in _chat_history:
        _chat_history[session_id] = []
    _chat_history[session_id].append({"role": role, "content": content})

def get_all_sessions() -> list:
    """获取所有有聊天记录的用户 ID 列表"""
    return list(_chat_history.keys())

def clear_history(session_id: str):
    """清空某个用户的聊天记录"""
    if session_id in _chat_history:
        del _chat_history[session_id]