# app.py
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1 import auth, classes, health, users
from core.exception_handlers import register_exception_handlers
from core.logger import setup_logging
from core.middleware import AccessLogMiddleware
from db.connector import DatabaseConnector

logo = r"""
$$$$$$$$\      $$\           $$$$$$$\  $$\ $$\            $$\     
$$  _____|     $$ |          $$  __$$\ \__|$$ |           $$ |    
$$ |      $$$$$$$ |$$\   $$\ $$ |  $$ |$$\ $$ | $$$$$$\ $$$$$$\   
$$$$$\   $$  __$$ |$$ |  $$ |$$$$$$$  |$$ |$$ |$$  __$$\\_$$  _|  
$$  __|  $$ /  $$ |$$ |  $$ |$$  ____/ $$ |$$ |$$ /  $$ | $$ |    
$$ |     $$ |  $$ |$$ |  $$ |$$ |      $$ |$$ |$$ |  $$ | $$ |$$\ 
$$$$$$$$\\$$$$$$$ |\$$$$$$  |$$ |      $$ |$$ |\$$$$$$  | \$$$$  |
\________|\_______| \______/ \__|      \__|\__| \______/   \____/ 
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 生命周期事件，用于初始化数据库连接等
    """
    setup_logging()
    await DatabaseConnector.initialize()
    yield
    await DatabaseConnector.engine.dispose()  # 清理资源


app = FastAPI(
    title="EduPilot",
    version="0.1a",
    reload=True,
    lifespan=lifespan,
    docs_url=None,  # 关闭 Swagger UI
    redoc_url=None,  # 关闭 ReDoc
    openapi_url=None,  # 关闭 OpenAPI JSON 接口（连接口也关闭）
)
# 注册路由
app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])
app.include_router(users.router, prefix="/api/v1", tags=["Users"])
app.include_router(classes.router, prefix="/api/v1", tags=["Classes"])
app.include_router(health.router, prefix="", tags=["Health"])
app.add_middleware(AccessLogMiddleware)


register_exception_handlers(app)

origins = [
    "http://localhost:5173",
    # 如果有多个前端，可以继续添加
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # ⬅️ 正确写法：直接传递 origins 列表
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to EduPilot API 👋"}


if __name__ == "__main__":
    print(logo)
    uvicorn.run(
        "app:app",
        host=os.getenv("APP_HOST", "127.0.0.1"),
        port=int(os.getenv("APP_PORT", 8000)),
        reload=bool(os.getenv("APP_RELOAD", "false")),
        server_header=False,
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
        reload_excludes=["**/logs/*", "**/*.log"],
    )
