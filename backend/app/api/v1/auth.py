# routers/auth.py
import logging
from typing import Union

from fastapi import APIRouter, Cookie, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from core.rate_limit import rate_limiter
from core.response import to_response
from db.connector import DatabaseConnector
from schemas.Request import LoginRequest
from schemas.Response import ApiResponse, ErrorResponse, LoginData, LoginResponse
from schemas.User import User
from services.auth import authenticate_user, get_user_by_uuid
from utils.token import create_access_token, create_fresh_token, verify_fresh_token

router = APIRouter(prefix="/auth", tags=["Auth"])

logger = logging.getLogger("api.v1.auth")


@router.post(
    "/login",
    dependencies=[Depends(rate_limiter(limit=10, windows=60))],
    response_model=Union[LoginResponse, ErrorResponse],
)
async def login_route(
    form_data: LoginRequest, db: AsyncSession = Depends(DatabaseConnector.get_db)
):
    """
    用户登录接口

    验证用户名和密码，认证成功后生成 access token 和 refresh token。
    refresh_token 以 HttpOnly Cookie 的形式返回，access_token 包含在响应体中。

    - 请求频率限制：每分钟最多10次
    - 返回：LoginResponse 或 ErrorResponse
    """
    logger.info("登录请求: 用户名:%s", form_data.username)
    user = await authenticate_user(db, form_data.username, form_data.password)

    token, expires_in = create_access_token({"uuid": str(user.uuid)})
    refresh_token, refresh_expires_in = create_fresh_token({"uuid": str(user.uuid)})

    logger.info("登录成功: 用户名: %s, UUID: %s", user.username, user.uuid)
    response = to_response(
        data=LoginData(
            access_token=token, expires_in=expires_in, user=User.model_validate(user)
        ),
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=refresh_expires_in,
        httponly=True,
        secure=True,
        samesite="Lax",
        path="/api/v1/auth/refresh",
    )

    return response


@router.get("/profile", response_model=Union[ApiResponse, ErrorResponse])
async def profile_route(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户信息

    通过 access_token 验证后，返回用户基础信息。

    - 需要提供有效的 access_token
    - 返回：ApiResponse 包含用户信息，或 ErrorResponse
    """
    logger.info(
        "获取用户信息成功: 用户名: %s, UUID: %s",
        current_user.username,
        current_user.uuid,
    )
    return to_response(data=User.model_validate(current_user))


@router.post(
    "/refresh",
    # dependencies=[Depends(rate_limiter(limit=10, windows=60))],
    response_model=Union[LoginResponse, ErrorResponse],
)
async def refresh_token_route(
    refresh_token: str = Cookie(...),
    db: AsyncSession = Depends(DatabaseConnector.get_db),
):
    """
    刷新 access token 接口

    从 Cookie 中读取 fresh_token（HttpOnly），验证通过后签发新的 access_token。

    - 适用于 access_token 过期但 fresh_token 仍有效的场景
    - 返回：新的 access_token 及用户信息
    - 请求频率限制：每分钟最多10次
    """

    payload = verify_fresh_token(refresh_token)
    user = await get_user_by_uuid(db, payload["uuid"])
    new_token, expires_in = create_access_token({"uuid": str(user.uuid)})
    logger.info(
        "刷新令牌成功: 用户名: %s, UUID: %s, 新令牌: %s",
        user.username,
        user.uuid,
        new_token,
    )
    return to_response(
        message="Token refreshed successfully",
        data=LoginData(
            access_token=new_token,
            expires_in=expires_in,
            user=User.model_validate(user),
        ),
    )


@router.get("/verify_token", response_model=Union[ApiResponse, ErrorResponse])
async def verify_token_route(current_user: User = Depends(get_current_user)):
    """
    验证 access token 接口

    用于判断 access_token 是否有效，常用于前端页面刷新时验证会话是否仍然有效。

    - 返回：验证通过则返回 "Token is valid"，否则返回错误信息
    """

    logger.info(
        "令牌验证成功: 用户名: %s, UUID: %s", current_user.username, current_user.uuid
    )
    return to_response(message="Token is valid")


@router.post("/logout", response_model=Union[ApiResponse, ErrorResponse])
async def logout_route():
    response= to_response()
    response.delete_cookie(key="refresh_token", path="/api/v1/auth/refresh")
    return response