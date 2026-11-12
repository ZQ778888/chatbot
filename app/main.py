from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import chat
from app.database import init_db

app = FastAPI(title="聊天机器人接口")


@app.on_event("startup")
def startup():
    init_db()


app.include_router(chat.router)

# 托管静态前端页面，注意要放在路由之后
# check_dir=False：static 目录稍后随前端提交加入，这里先避免目录不存在时启动报错
app.mount("/", StaticFiles(directory="static", html=True, check_dir=False), name="static")
