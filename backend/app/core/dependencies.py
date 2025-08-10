# core/dependencies.py
import logging

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core import exceptions
from db.connector import DatabaseConnector
from models.user import User
from schemas.User import User
from services.auth import get_user_by_uuid
from utils.token import verify_access_token

logger = logging.getLogger("core.dependencies")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(DatabaseConnector.get_db),
) -> User | None:
    """
    从请求中提取访问令牌，验证其有效性，并返回对应的用户对象。

    参数说明:
        token (str): 从请求头中自动注入的 Bearer Token（由 OAuth2PasswordBearer 提供）
        db (Session): 注入的数据库会话对象（通过依赖注入提供）

    返回值:
        User | None: 成功验证令牌并查找到用户时返回 User 对象；验证失败则抛出异常。

    异常说明:
        - InvalidVerifyToken: 令牌无效、缺失或格式错误
        - NotExists: 数据库中不存在与令牌中 UUID 匹配的用户
        - DatabaseQueryError: 查询过程中发生数据库访问异常

    使用场景:
        - 作为路由依赖项（Depends），用于确保当前请求用户已登录并且令牌有效。
        - 常用于需要身份认证的接口，如获取个人资料、修改密码等。

    日志行为:
        - 成功验证令牌并查询用户时记录 info 级别日志。
        - 用户不存在记录 warning。
        - 未知异常记录 error，包含完整堆栈。
    """
    try:
        logger.info("验证访问令牌")
        token_data = verify_access_token(token)
        if not token_data or not token_data.get("uuid"):
            raise exceptions.InvalidVerifyToken("令牌无效或缺少uuid")
        user = await get_user_by_uuid(db, token_data.get("uuid"))
        logger.info(
            "访问令牌验证成功: uuid: %s 用户名: %s",
            getattr(user, "uuid", None),
            getattr(user, "username", None),
        )
        return user
    except exceptions.InvalidVerifyToken:
        raise
    except exceptions.NotExists:
        logger.info("用户不存在")
        raise
    except Exception as e:
        logger.error("未知错误: %s", e, exc_info=True)
        raise exceptions.DatabaseQueryError("数据库访问失败") from e
