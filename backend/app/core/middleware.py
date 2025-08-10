import logging
import time
import traceback

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# 初始化中间件的专属 logger
logger = logging.getLogger("core.middleware")


class AccessLogMiddleware(BaseHTTPMiddleware):
    """
    请求访问日志中间件：
    - 记录每一个 HTTP 请求的开始、结束、耗时、状态码。
    - 捕获异常时打印详细堆栈，辅助调试。
    """

    async def dispatch(self, request: Request, call_next):
        # 记录请求开始时间（用于计算耗时）
        start_time = time.time()

        # 获取客户端 IP（支持通过反向代理获取真实 IP）
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            # 若有多个 IP（经过多级代理），取最前面的一个
            client_ip = x_forwarded_for.split(",")[0].strip()
        else:
            # 默认使用 FastAPI 记录的客户端地址
            client_ip = request.client.host

        method = request.method  # 请求方法（GET、POST 等）
        path = request.url.path  # 请求路径

        # 打印请求开始日志
        logger.info(f"请求开始 - {client_ip} {method} {path}")

        try:
            # 调用后续中间件或路由处理函数
            response = await call_next(request)
        except Exception as exc:
            # 异常处理：打印堆栈信息以便排查问题
            tb = traceback.format_exc()
            logger.error(
                f"请求异常 - {client_ip} {method} {path} 错误: {exc}\n堆栈信息:\n{tb}"
            )
            raise  # 将异常继续抛出，由上层处理

        # 请求处理完成，计算耗时（单位：毫秒）
        process_time_ms = (time.time() - start_time) * 1000
        status_code = response.status_code

        # 打印请求结束日志（含状态码与耗时）
        logger.info(
            f"请求结束 - {client_ip} {method} {path} 状态码: {status_code} 耗时: {process_time_ms:.2f}ms"
        )

        return response  # 返回响应给客户端
