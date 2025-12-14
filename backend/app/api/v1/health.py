# routers/health.py
from fastapi import APIRouter
from starlette.responses import JSONResponse

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("", summary="健康检查", description="返回服务是否正常运行")
async def health_check():
    """
    健康检查接口，用于验证服务的基本可用性。

    主要流程：
    1. 不依赖任何参数或权限校验，直接响应固定内容。
    2. 返回一个简单的 JSON，字段包含：
       - `status`: 表示服务当前状态，正常运行时为 `"ok"`。
    3. 通常用于监控系统、负载均衡或外部服务检查本服务是否在线。

    返回：
        JSONResponse: 包含服务状态字段的基础健康检查结果。
    """
    return JSONResponse(content={"status": "ok"})
