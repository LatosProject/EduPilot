# services/auth.py
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core import exceptions
from models.user import User
from schemas.Response import UpdateUserData
from utils.auth_utils import hash_password, verify_password
from utils.random import generate_uuid

logger = logging.getLogger("services.auth")


async def get_user_by_username(db: AsyncSession, username: str) -> User:
    """
    根据用户名查询用户信息。

    参数说明:
        db (AsyncSession): 异步数据库会话
        username (str): 用户名

    返回值:
        User: 查询到的用户对象

    异常说明:
        - NotExists: 用户不存在
        - DatabaseQueryError: 数据库执行失败

    其他说明:
        查询失败将统一抛出封装异常，供上层逻辑处理。
    """
    logger.info("使用 用户名 查询用户: %s", username)
    try:
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
    except Exception as e:
        logger.error("数据库查询异常: 用户名: %s, 错误: %s", username, e)
        raise exceptions.DatabaseQueryError() from e
    if user is None:
        raise exceptions.AuthenticationFailed()
    return user


async def get_user_by_uuid(db: AsyncSession, uuid: str) -> User | None:
    """
    根据 UUID 查询用户信息。

    参数说明:
        db (AsyncSession): 异步数据库会话
        uuid (str): 用户唯一标识符

    返回值:
        User: 查询到的用户对象

    异常说明:
        - NotExists: 用户不存在
        - DatabaseQueryError: 数据库执行失败
    """
    logger.info("使用 UUID 查询用户 %s", uuid)
    try:
        stmt = select(User).filter(User.uuid == uuid)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
    except Exception as e:
        logger.error("数据库查询异常: UUID: %s, 错误: %s", uuid, e)
        raise exceptions.DatabaseQueryError() from e
    if user is None:
        raise exceptions.NotExists(uuid=uuid)
    return user


async def get_user_role_by_uuid(db: AsyncSession, uuid: str) -> str | None:
    """
    获取指定 UUID 对应用户的角色。

    参数说明:
        db (AsyncSession): 异步数据库会话
        uuid (str): 用户唯一标识符

    返回值:
        str | None: 用户角色，若用户不存在返回 None

    异常说明:
    -  数据库错误时抛出 DatabaseQueryError，调用者需捕获
    """
    logger.info("使用 UUID 查询用户角色: UUID: %s", uuid)
    try:
        stmt = select(User).filter(User.uuid == uuid)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        return user.role if user else None
    except Exception as e:
        logger.error("数据库查询用户角色失败: UUID: %s, 错误: %s", uuid, e)
        raise exceptions.DatabaseQueryError() from e


async def create_user(
    db: AsyncSession,
    username: str,
    email: str,
    password: str,
    profile_name: str,
    avatar_url: str,
    role: str = "user",
) -> User | None:
    """
    创建新用户记录。

    参数说明:
        db (AsyncSession): 异步数据库会话
        username (str): 用户名
        email (str): 邮箱地址
        password (str): 原始密码（将被加密存储）
        profile_name (str): 用户个人资料名称
        avatar_url (str): 用户头像地址（可为空）
        role (str): 角色类型（默认 "user"）

    返回值:
        User | None: 成功创建则返回用户对象，失败返回 None

    异常说明:
        - AlreadyExists: 用户名或邮箱已存在（唯一性约束冲突）

    其他说明:
        - 密码将使用哈希函数加密存储
        - 若未提供头像或昵称，将使用默认值
    """
    logger.info("创建用户: 用户名: %s, 角色: %s", username, role)
    hashed_pw = hash_password(password)
    user = User(
        uuid=generate_uuid(),
        username=username,
        email=email,
        hashed_password=hashed_pw,
        role=role,
        status="active",
        created_at=datetime.now(timezone.utc),
        last_login=datetime.now(timezone.utc),
        profile_name=profile_name if profile_name else "User",  # 默认个人资料名称
        avatar_url=(
            avatar_url
            if avatar_url
            else "https://www.gstatic.com/images/branding/product/1x/avatar_circle_blue_512dp.png"
        ),  # 默认头像URL
    )
    try:
        logger.info("尝试添加用户到数据库: 用户名: %s", username)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError as e:
        await db.rollback()
        if "UNIQUE constraint failed" in str(e.orig):
            raise exceptions.AlreadyExists()
    except Exception as e:
        logger.error("添加用户到数据库失败: 用户名: %s, 错误: %s", username, e)
        raise exceptions.InvalidParameter()


async def delete_user(
    db: AsyncSession,
    user_uuid: str,
) -> None:
    """delete user by uuid

    Args:
        db (AsyncSession): 异步数据库会话
        user_uuid (str): 用户唯一标识符

    Raises:
        exceptions.InvalidParameter: HTTP 400, 用户不存在
        exceptions.NotExists: HTTP 404, 记录不存在
    """
    logger.info(f"删除用户请求: 用户UUID: {user_uuid}")
    user = await get_user_by_uuid(db, user_uuid)
    try:
        await db.delete(user)
        await db.commit()
    except Exception as e:
        logger.error("删除用户到数据库失败: 用户名: %s, 错误: %s", user.username, e)
        raise exceptions.InvalidParameter()
    logger.info(f"用户删除成功: 用户UUID: {user_uuid}")


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> User | None:
    """
    验证用户名和密码是否匹配。

    参数说明:
        db (AsyncSession): 异步数据库会话
        username (str): 登录用户名
        password (str): 登录密码

    返回值:
        User: 验证成功的用户对象

    异常说明:
        - NotExists: 用户不存在
        - AuthenticationFailed: 密码验证失败
        - DatabaseQueryError: 查询过程中发生数据库错误
    """
    logger.info(f"尝试登录: 用户名: {username}")
    try:
        user = await get_user_by_username(db, username)
    except exceptions.BaseAppException as e:
        raise e
    except Exception as e:
        logger.error(f"数据库查询异常，登录失败: 用户名: {username} 错误: {e}")
        raise exceptions.DatabaseQueryError() from e
    if not verify_password(password, user.hashed_password):
        raise exceptions.AuthenticationFailed(username=username)
    return user


async def update_user(
    db: AsyncSession,
    user_uuid: str,
    current_role: str,
    username: Optional[str] = None,
    role: Optional[str] = None,
    email: Optional[str] = None,
    status: Optional[str] = None,
    profile_name: Optional[str] = None,
    avatar_url: Optional[str] = None,
):
    """
    灵活地更新用户信息，只更新提供了新值的字段。

    主要流程：
    1. 根据 user_uuid 从数据库获取用户对象。
    2. 对每个传入的非 None 参数进行检查，并更新用户对象的相应属性。
    3. 如果当前用户角色是 "admin"，则允许更新敏感信息（用户名、角色、状态）。
    4. 提交数据库事务，如果发生唯一约束冲突则回滚并抛出 AlreadyExists 异常。
    5. 如果发生其他异常，则回滚并记录日志，抛出 InvalidParameter 异常。
    6. 成功后，将更新后的用户对象属性映射到 UpdateUserData 模型并返回。

    参数：
        db (AsyncSession): 数据库会话。
        user_uuid (str): 要更新的用户的唯一标识符。
        current_role (str): 执行此操作的用户的角色。
        username (Optional[str]): 可选的新用户名。
        new_role (Optional[str]): 可选的新用户角色。
        email (Optional[str]): 可选的新邮箱。
        status (Optional[str]): 可选的新用户状态。
        profile_name (Optional[str]): 可选的新个人资料名称。
        avatar_url (Optional[str]): 可选的新头像 URL。

    返回：
        UpdateUserData: 包含更新后用户信息的 Pydantic 模型。

    异常：
        - AlreadyExists: 如果更新的用户名或邮箱已存在。
        - InvalidParameter: 如果发生其他数据库错误。
    """
    try:
        user_obj = await get_user_by_uuid(db, user_uuid)
        # 更新非敏感信息
        if email is not None:
            user_obj.email = email
        if profile_name is not None:
            user_obj.profile_name = profile_name
        if avatar_url is not None:
            user_obj.avatar_url = avatar_url

        # 仅当当前用户是管理员时，才允许更新敏感信息
        if current_role == "admin":
            if role is not None:
                user_obj.role = role
            if username is not None:
                user_obj.username = username
            if status is not None:
                user_obj.status = status
        await db.commit()
        await db.refresh(user_obj)
        return UpdateUserData(
            username=user_obj.username,
            email=user_obj.email,
            profile_name=user_obj.profile_name,
            avatar_url=user_obj.avatar_url,
            role=user_obj.role,
            status=user_obj.status,
        )
    except IntegrityError as e:
        await db.rollback()
        if "UNIQUE constraint failed" in str(e.orig):
            raise exceptions.AlreadyExists()
    except Exception as e:
        await db.rollback()
        logger.error("添加新用户信息到数据库失败, 错误: %s", e)
        raise exceptions.InvalidParameter()
