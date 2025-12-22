import json
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import logger
from sqlalchemy import and_, asc, desc, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core import exceptions
from models.class_model import (
    AssignmentModel,
    ClassMemberModel,
    ClassModel,
    AssignmentSubmissionModel,
)
from models.user import User
from schemas.Response import ClassUserData, Attachment
from utils import random

logger = logging.getLogger("services.classes")


async def get_class_by_uuid(db: AsyncSession, class_uuid: str) -> ClassModel:
    """
    根据 class_uuid 查询班级信息。

    参数说明:
        db (AsyncSession): 异步数据库会话
        class_uuid (str): 班级唯一标识符

    返回值:
        Class: 查询到的班级对象

    异常说明:
        - NotExists: 班级不存在
        - DatabaseQueryError: 数据库查询失败
    """
    logger.debug("查询班级信息: %s", class_uuid)
    try:
        stmt = select(ClassModel).where(ClassModel.class_uuid == class_uuid)
        result = await db.execute(stmt)
        class_obj = result.scalar_one_or_none()
    except Exception as e:
        logger.error("查询班级失败: %s, 错误: %s", class_uuid, e)
        raise exceptions.DatabaseQueryError("查询班级信息失败") from e

    if class_obj is None:
        raise exceptions.InvalidParameter("班级不存在")

    return class_obj


async def create_class(
    db: AsyncSession, class_name: str, description: str, teacher_uuid: str
) -> ClassModel | None:
    """
    创建新班级记录

    参数:
        db (AsyncSession): 数据库会话（异步）
        class_name (str): 班级名称
        description (str): 班级描述
        teacher_uuid (str): 班主任用户的 UUID

    返回:
        ClassModel | None: 创建成功则返回班级模型实例；若已存在则抛出异常
    """
    new_class = ClassModel(
        class_name=class_name,
        description=description,
        teacher_uuid=teacher_uuid,
        invite_code=random.generate_invite_code(),
    )
    try:
        logger.info("尝试添加新班级到数据库: 班级名: %s", class_name)
        db.add(new_class)
        await db.commit()
        await db.refresh(new_class)
        return new_class
    except IntegrityError as e:
        await db.rollback()
        if "UNIQUE constraint failed" in str(e.orig):
            raise exceptions.AlreadyExists()
    except Exception as e:
        logger.error("添加新班级到数据库失败, 错误: %s", e)
        raise exceptions.InvalidParameter()


async def delete_class(
    db: AsyncSession, class_uuid: str, user_uuid: str, user_role: str
) -> None:
    """
    删除指定班级（支持管理员或班主任操作）

    参数:
        db (AsyncSession): 异步数据库会话
        class_uuid (str): 班级唯一标识符
        user_uuid (str): 请求用户的 UUID
        user_role (str): 请求用户的角色（admin 或 teacher）

    异常:
        - 如果用户无权限，将抛出 NotFound 或 InvalidParameter 异常
        - 发生数据库错误时抛出 InvalidParameter 异常
    """
    if not user_role == "admin":
        get_class_member_by_uuid(db, class_uuid, user_uuid)
    try:
        class_to_delete = await get_class_by_uuid(db, class_uuid)
        await db.delete(class_to_delete)
        await db.commit()
    except Exception as e:
        logger.error("删除班级到数据库失败: 班级ID: %s, 错误: %s", class_uuid, e)
        raise exceptions.InvalidParameter()
    logger.info(f"用户删除成功: 班级UUID: {class_uuid}")


async def create_assignment(
    db: AsyncSession,
    class_uuid: str,
    title: str,
    description: str,
    content: str,
    status: str,
    deadline: str,
    max_score: int,
    allow_late_submission: bool,
    created_by: str,
    attachments: list[Attachment] | None = None,
):
    """
    创建新的作业记录，并保存到数据库。

    该函数会校验目标班级是否存在，然后基于传入的字段构建作业数据模型，并写入数据库。
    若作业已存在（如 UUID 或其他唯一约束冲突），会抛出 AlreadyExists 异常。
    所有异常会记录日志，事务失败时自动回滚。

    参数:
        db (AsyncSession): 数据库异步会话，用于执行写入操作。
        class_uuid (str): 作业所属的班级 UUID。必须是存在的班级，否则抛出异常。
        title (str): 作业标题，通常要求在班级中具有唯一性。
        description (str): 作业摘要，用于简要说明内容。
        content (str): 作业正文，支持富文本或 markdown。
        status (str): 作业状态，推荐使用枚举值（如 "draft", "published"）。
        deadline (str): 截止日期，建议传入 ISO 8601 格式的字符串。
        max_score (int): 作业满分，必须为非负整数。
        allow_late_submission (bool): 是否允许迟交。为 True 表示过期仍可提交。
        attachments (list[str]): 附件列表，格式为 URL 或文件名数组。
        created_by (str): 创建该作业的用户 UUID，通常为教师或管理员。

    返回:
        AssignmentModel: 创建成功的作业对象，包含数据库自动生成的字段（如主键、时间戳等）。

    异常:
        AlreadyExists: 若违反唯一性约束（如标题重复）则抛出。
        InvalidParameter: 捕捉所有其他非法参数或数据库写入失败的场景。

    注意事项:
        - deadline 应与数据库模型字段类型保持一致（datetime），如传入字符串需确保格式正确或转换。
        - attachments 字段应为 JSON 可序列化格式（如字符串列表）。
        - 数据提交前已通过 get_class_by_uuid 验证班级存在性，避免外键错误。
        - 所有数据库操作失败均会自动 rollback，确保数据一致性。
    """
    attachments_json = json.dumps(
        [{**a.dict(), "url": str(a.url)} for a in attachments] if attachments else [],
        separators=(",", ":"),
    )

    await get_class_by_uuid(db, class_uuid)
    new_assignment = AssignmentModel(
        uuid=random.generate_uuid(),
        class_uuid=class_uuid,
        title=title,
        description=description,
        content=content,
        status=status,
        deadline=deadline,
        max_score=max_score,
        allow_late_submission=allow_late_submission,
        attachments=attachments_json,
        submission_count=0,
        updated_at=datetime.now(timezone.utc),
        created_by=created_by,
        created_at=datetime.now(timezone.utc),
    )
    try:
        logger.info("尝试添加新作业到数据库: 作业名: %s", title)
        db.add(new_assignment)
        await db.commit()
        await db.refresh(new_assignment)
        return new_assignment
    except IntegrityError as e:
        await db.rollback()
        if "UNIQUE constraint failed" in str(e.orig):
            raise exceptions.AlreadyExists()
    except Exception as e:
        logger.error("添加新作业到数据库失败, 错误: %s", e)
        raise exceptions.InvalidParameter()
    pass


async def get_assignment(
    db: AsyncSession, assignment_uuid: str, class_uuid: str, user_uuid: str
):
    """
    获取指定班级内的单个作业详情。

    该函数会先验证用户是否为班级成员，然后根据作业 UUID 与班级 UUID 查询目标作业。
    若作业不存在，将抛出 NotExists 异常；若查询数据库失败，将抛出 DatabaseQueryError 异常。

    参数:
        db (AsyncSession): 异步数据库会话。
        assignment_uuid (str): 要查询的作业唯一标识符（UUID）。
        class_uuid (str): 作业所属班级的 UUID。
        user_uuid (str): 当前请求用户的 UUID，用于验证是否属于该班级。

    返回:
        AssignmentModel: 作业对象，若存在并查询成功。

    异常:
        NotExists: 若作业不存在或不属于该班级。
        DatabaseQueryError: 数据库查询过程中发生未知错误。
        NotClassMember: 若用户不是该班级成员（由 get_class_member_by_uuid 抛出）。
    """
    await get_class_member_by_uuid(db, class_uuid, user_uuid)

    logger.debug("正在查询作业: uuid: %s, class: %s", assignment_uuid, class_uuid)

    try:
        stmt = select(AssignmentModel).where(
            AssignmentModel.uuid == assignment_uuid,
            AssignmentModel.class_uuid == class_uuid,
        )
        result = await db.execute(stmt)
        assignment = result.scalar_one_or_none()
    except Exception as e:
        logger.error("查询作业失败: %s", e)
        raise exceptions.DatabaseQueryError("查询作业信息失败") from e

    if assignment is None:
        raise exceptions.NotExists()

    # 标记该作业是否被当前用户提交过
    try:
        res = await db.execute(
            select(AssignmentSubmissionModel).where(
                AssignmentSubmissionModel.assignment_uuid == assignment_uuid,
                AssignmentSubmissionModel.user_uuid == user_uuid,
            )
        )
        submitted = res.scalar_one_or_none() is not None
    except Exception:
        submitted = False
    setattr(assignment, "submitted", submitted)

    return assignment


async def get_class_member_by_uuid(
    db: AsyncSession, class_uuid: str | None = None, user_uuid: str | None = None
):
    """
    根据班级 UUID 和用户 UUID 查询班级成员信息。

    用途：
        - 验证某个用户是否属于某个班级
        - 查询某个班级的所有成员
        - 查询某个用户所在的所有班级

    参数:
        db (AsyncSession): 异步数据库会话，用于执行 SQL 查询
        class_uuid (str | None): 班级唯一标识符，可选
        user_uuid (str | None): 用户唯一标识符，可选

    返回:
        list[ClassMemberModel]: 查询到的班级成员对象列表（至少有一条记录）

    异常:
        InvalidParameter: 当两个参数都未传入，或未查到任何成员时抛出
        DatabaseQueryError: 当执行数据库查询时发生异常抛出
    """
    try:
        conditions = []
        if user_uuid:
            conditions.append(ClassMemberModel.user_uuid == user_uuid)
        if class_uuid:
            conditions.append(ClassMemberModel.class_uuid == class_uuid)

        stmt = select(ClassMemberModel)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        result = await db.execute(stmt)
        members = result.scalars().all()
    except Exception as e:
        logger.error("查询班级成员失败: %s，错误: %s", user_uuid, e)
        raise exceptions.DatabaseQueryError("查询班级成员失败") from e

    if not members:
        raise exceptions.InvalidParameter()

    return members


async def get_class_by_invite_code(db: AsyncSession, invite_code: str):
    """
    通过邀请码查询对应的班级信息。

    参数:
        db (AsyncSession): 异步数据库会话，用于执行查询。
        invite_code (str): 班级邀请码，唯一标识。

    返回:
        ClassModel: 对应的邀请码所关联的班级对象。

    异常:
        InvalidParameter: 若未找到对应的班级，表示邀请码无效。
    """
    stmt = select(ClassModel).where(ClassModel.invite_code == invite_code)
    result = await db.execute(stmt)
    class_obj = result.scalar_one_or_none()
    if not class_obj:
        raise exceptions.InvalidParameter()
    return class_obj


async def join_class(db: AsyncSession, invite_code: str, current_user: User):
    """
    用户通过邀请码加入班级。

    流程说明：
    1. 通过邀请码查找对应班级。
    2. 检查用户是否已经是该班级成员，防止重复加入。
    3. 若未加入，则创建新的班级成员记录，默认角色为学生。
    4. 提交数据库事务并刷新对象状态，返回成员信息。

    参数：
        db (AsyncSession): 异步数据库会话。
        invite_code (str): 班级邀请码，用于查找对应班级。
        current_user (User): 当前请求的用户对象。

    返回：
        ClassUserData: 新加入的班级成员数据，包含角色、班级ID、用户ID、用户昵称和加入时间。

    异常：
        AlreadyExists: 用户已是该班级成员时抛出。
        InvalidParameter: 邀请码无效或对应班级不存在。
        DatabaseQueryError: 数据库操作失败或其他未知异常。
    """
    try:
        class_obj = await get_class_by_invite_code(db, invite_code)
        class_uuid = str(class_obj.class_uuid)
        stmt = select(ClassMemberModel).where(
            ClassMemberModel.class_uuid == class_uuid,
            ClassMemberModel.user_uuid == current_user.uuid,
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            raise exceptions.AlreadyExists("您已经加入该班级")
        new_member = ClassMemberModel(
            created_at=datetime.now(timezone.utc),
            role="student",
            class_uuid=class_uuid,
            user_uuid=current_user.uuid,
        )
        db.add(new_member)
        await db.commit()
        # NOTE:根据SQL库源码显示，commit后所有会话将会标为已过期，这将无法再操作sql对象。所以需要refresh重新刷新
        await db.refresh(new_member)
        await db.refresh(current_user)
        return ClassUserData(
            role=new_member.role,
            class_uuid=new_member.class_uuid,
            user_uuid=current_user.uuid,
            profile_name=current_user.profile_name,
            created_at=new_member.created_at,
        )

    except exceptions.AlreadyExists as e:
        logger.warning(f"加入班级失败: {e}")
        raise e
    except IntegrityError as e:
        await db.rollback()
        if "UNIQUE constraint failed" in str(e.orig):
            raise exceptions.AlreadyExists("您已经加入该班级")
        logger.error(
            "数据库完整性错误: user=%s, invite_code=%s, 错误=%s",
            current_user.uuid,
            invite_code,
            e,
        )
        raise exceptions.DatabaseQueryError("数据库操作失败")
    except exceptions.InvalidParameter as e:
        logger.warning(
            "加入班级失败: user=%s, invite_code=%s",
            current_user.uuid,
            invite_code,
        )
        raise exceptions.InvalidParameter("无效的邀请码")
    except Exception as e:
        await db.rollback()
        raise exceptions.DatabaseQueryError("加入班级失败")


async def get_assignments(
    user_uuid: str,
    db: AsyncSession,
    class_uuid: str,
    page: int,
    size: int,
    status: Optional[str],
    search: Optional[str],
    order_by: str,
    order: str,
):
    """
    获取指定班级的作业列表，支持分页、筛选、模糊搜索及排序。

    主要流程：
    1. 校验用户是否为该班级成员，非成员无权访问。
    2. 根据分页参数计算偏移量。
    3. 根据传入的筛选条件（状态、搜索关键字）构造查询。
    4. 根据排序字段及方向排序。
    5. 执行分页查询获取作业列表。
    6. 查询满足条件的作业总数，用于前端分页展示。

    参数：
        user_uuid (str): 当前请求用户的 UUID。
        db (AsyncSession): 异步数据库会话。
        class_uuid (str): 目标班级 UUID。
        page (int): 页码，从 1 开始。
        size (int): 每页记录数。
        status (Optional[str]): 作业状态过滤（可选，如 'published'）。
        search (Optional[str]): 模糊搜索关键词（匹配标题或描述）。
        order_by (str): 排序字段名（必须是 AssignmentModel 的属性）。
        order (str): 排序方向，'asc' 升序或 'desc' 降序。

    返回：
        tuple: (items, total)
            - items (List[AssignmentModel]): 当前页查询到的作业列表。
            - total (int): 满足条件的作业总数，用于分页计算。

    异常：
        - 若用户非班级成员，将由 get_class_member_by_uuid 抛出异常。
        - 查询过程中可能抛出数据库异常。
    """
    await get_class_member_by_uuid(db, class_uuid, user_uuid)
    # 偏移量
    offset = (page - 1) * size
    stmt = select(AssignmentModel).where(AssignmentModel.class_uuid == class_uuid)

    # 状态过滤（支持前端自定义的筛选：pending / done / expired）
    if status:
        # 前端使用 'done' 来表示学生已提交的作业；'pending' 表示未过期且未提交；'expired' 表示已过期且未提交
        now = datetime.now(timezone.utc)
        if status == "done":
            # 仅返回当前用户已提交的作业
            subq = (
                select(AssignmentSubmissionModel.assignment_uuid)
                .where(AssignmentSubmissionModel.user_uuid == user_uuid)
                .scalar_subquery()
            )
            stmt = stmt.where(AssignmentModel.uuid.in_(subq))
        elif status == "pending":
            # 截止时间在现在或之后，且当前用户尚未提交
            subq = (
                select(AssignmentSubmissionModel.assignment_uuid)
                .where(AssignmentSubmissionModel.user_uuid == user_uuid)
                .scalar_subquery()
            )
            stmt = stmt.where(AssignmentModel.deadline >= now).where(
                ~AssignmentModel.uuid.in_(subq)
            )
        elif status == "expired":
            # 截止时间在现在之前，且当前用户尚未提交
            subq = (
                select(AssignmentSubmissionModel.assignment_uuid)
                .where(AssignmentSubmissionModel.user_uuid == user_uuid)
                .scalar_subquery()
            )
            stmt = stmt.where(AssignmentModel.deadline < now).where(
                ~AssignmentModel.uuid.in_(subq)
            )
        else:
            # fallback：按数据库中 AssignmentModel.status 字段过滤
            stmt = stmt.where(AssignmentModel.status == status)

    # 模糊搜索（匹配 title、description 或 content）
    if search:
        stmt = stmt.where(
            or_(
                AssignmentModel.title.ilike(f"%{search}%"),
                AssignmentModel.description.ilike(f"%{search}%"),
                AssignmentModel.content.ilike(f"%{search}%"),
            )
        )
    # 排序字段和方向
    order_column = getattr(AssignmentModel, order_by, None)
    if order_column is not None:
        stmt = stmt.order_by(
            desc(order_column) if order == "desc" else asc(order_column)
        )

    # 分页
    stmt = stmt.offset(offset).limit(size)

    # 查询数据
    result = await db.execute(stmt)
    items = result.scalars().all()

    # 为每个作业标记当前用户是否已提交
    if items:
        # 查询当前用户已提交的作业 UUID 列表
        submitted_uuids_stmt = select(AssignmentSubmissionModel.assignment_uuid).where(
            AssignmentSubmissionModel.user_uuid == user_uuid,
            AssignmentSubmissionModel.assignment_uuid.in_([item.uuid for item in items])
        )
        submitted_result = await db.execute(submitted_uuids_stmt)
        submitted_uuids = set(submitted_result.scalars().all())

        # 为每个作业设置 submitted 属性
        for item in items:
            setattr(item, "submitted", item.uuid in submitted_uuids)

    # 总数查询（用于分页）
    count_stmt = (
        select(func.count())
        .select_from(AssignmentModel)
        .where(AssignmentModel.class_uuid == class_uuid)
    )

    if status:
        now = datetime.now(timezone.utc)
        if status == "done":
            subq = (
                select(AssignmentSubmissionModel.assignment_uuid)
                .where(AssignmentSubmissionModel.user_uuid == user_uuid)
                .scalar_subquery()
            )
            count_stmt = count_stmt.where(AssignmentModel.uuid.in_(subq))
        elif status == "pending":
            subq = (
                select(AssignmentSubmissionModel.assignment_uuid)
                .where(AssignmentSubmissionModel.user_uuid == user_uuid)
                .scalar_subquery()
            )
            count_stmt = count_stmt.where(AssignmentModel.deadline >= now).where(
                ~AssignmentModel.uuid.in_(subq)
            )
        elif status == "expired":
            subq = (
                select(AssignmentSubmissionModel.assignment_uuid)
                .where(AssignmentSubmissionModel.user_uuid == user_uuid)
                .scalar_subquery()
            )
            count_stmt = count_stmt.where(AssignmentModel.deadline < now).where(
                ~AssignmentModel.uuid.in_(subq)
            )
        else:
            count_stmt = count_stmt.where(AssignmentModel.status == status)
    if search:
        count_stmt = count_stmt.where(
            or_(
                AssignmentModel.title.ilike(f"%{search}%"),
                AssignmentModel.description.ilike(f"%{search}%"),
                AssignmentModel.content.ilike(f"%{search}%"),
            )
        )

    total = (await db.execute(count_stmt)).scalar_one()

    return items, total


async def get_users(
    db: AsyncSession,
    status: Optional[str],
    search: Optional[str],
    role: str,
    page: int,
    size: int,
):
    """
    查询用户列表，支持分页、按状态、角色筛选及模糊搜索。

    主要流程：
    1. 根据分页参数计算偏移量。
    2. 构造查询条件，支持状态过滤、角色过滤和关键词模糊匹配（用户名、昵称、邮箱）。
    3. 执行分页查询获取符合条件的用户列表。
    4. 执行统计查询获取满足条件的用户总数，方便分页展示。

    参数：
        db (AsyncSession): 异步数据库会话，用于执行查询。
        status (Optional[str]): 用户状态筛选（如 "active", "inactive"），可选。
        search (Optional[str]): 模糊搜索关键字，匹配用户名、昵称或邮箱。
        role (str): 用户角色筛选，必须传入。
        page (int): 页码，从1开始。
        size (int): 每页条数。

    返回：
        tuple: (items, total)
            - items (List[User]): 当前页符合条件的用户对象列表。
            - total (int): 满足查询条件的用户总数。

    异常：
        - 可能抛出数据库操作相关异常。
    """
    # 偏移量
    offset = (page - 1) * size

    stmt = select(User)
    # 状态过滤（如 status='active'）
    if status:
        stmt = stmt.where(User.status == status)
    if role:
        stmt = stmt.where(User.role == role)
    # 模糊搜索（匹配 profile_name 或 email)
    if search:
        stmt = stmt.where(
            or_(
                User.profile_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.username.ilike(f"%{search}%"),
            )
        )
    # 分页
    stmt = stmt.offset(offset).limit(size)
    # 查询数据
    result = await db.execute(stmt)
    items = result.scalars().all()
    # 总数查询（用于分页）
    count_stmt = select(func.count()).select_from(User)

    if status:
        count_stmt = count_stmt.where(User.status == status)
    if role:
        count_stmt = count_stmt.where(User.role == role)
    if search:
        count_stmt = count_stmt.where(
            or_(
                User.profile_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
            )
        )
    total = (await db.execute(count_stmt)).scalar_one()

    return items, total


async def update_class(
    db: AsyncSession,
    class_uuid: str,
    class_name: str,
    description: str,
    user_uuid: str,
    user_role: str,
):
    """
    更新班级信息，仅允许管理员或该班级成员执行此操作。

    主要流程：
    1. 如果当前用户不是管理员，则校验其是否为该班级成员（无权限将抛出异常）。
    2. 根据 class_uuid 获取目标班级对象，若不存在则抛出 NotFound 异常。
    3. 更新班级名称与描述字段。
    4. 尝试提交事务，捕获唯一约束冲突（班级名重复）并转换为业务异常。
    5. 所有失败情况均进行事务回滚，并记录日志。

    参数：
        db (AsyncSession): 异步数据库会话，用于执行查询与事务。
        class_uuid (str): 要更新的班级的唯一标识符。
        class_name (str): 新的班级名称。
        description (str): 新的班级描述。
        user_uuid (str): 当前执行操作的用户 UUID。
        user_role (str): 当前用户的角色（如 "admin"）。

    返回：
        None

    异常：
        - AlreadyExists: 如果班级名称已存在（违反唯一约束）。
        - NotFoundException: 如果班级或班级成员不存在。
        - InvalidParameter: 其他参数错误或未处理异常。
    """
    logger.debug("更新班级信息: %s", class_uuid)
    if not user_role == "admin":
        await get_class_member_by_uuid(db, class_uuid, user_uuid)
    try:
        class_obj = await get_class_by_uuid(db, class_uuid)
        class_obj.class_name = class_name
        class_obj.description = description
        await db.commit()
        await db.refresh(class_obj)
    except IntegrityError as e:
        await db.rollback()
        if "UNIQUE constraint failed" in str(e.orig):
            raise exceptions.AlreadyExists()
    except Exception as e:
        await db.rollback()
        logger.error("添加新班级信息到数据库失败, 错误: %s", e)
        raise exceptions.InvalidParameter()
    return class_obj


async def get_class(db: AsyncSession, class_uuid: str, user_role: str):
    """
    根据班级 UUID 获取班级信息。

    主要流程：
    1. 如果用户角色为“教师”，则校验其是否为该班级成员（无权限将抛出异常）。
    2. 根据 class_uuid 获取班级对象。
    3. 如果班级不存在，则抛出 NotFoundException。
    4. 成功获取后返回班级对象。
    5. 所有失败情况均进行异常处理和日志记录。

    参数：
        db (AsyncSession): 异步数据库会话，用于执行查询。
        class_uuid (str): 要查询的班级的唯一标识符。
        user_role (str): 当前用户的角色。
        user_uuid (str): 当前用户的唯一标识符，用于权限校验。

    返回：
        class_obj: 查询到的班级对象。

    异常：
        - NotFoundException: 如果班级或班级成员不存在。
        - DatabaseQueryError: 如果数据库查询失败。
    """
    if user_role == "teacher":
        await get_class_member_by_uuid(class_uuid)
    try:
        class_obj = await get_class_by_uuid(db, class_uuid)
    except Exception as e:
        logger.error("查询作业失败: %s", e)
        raise exceptions.DatabaseQueryError("查询作业信息失败") from e
    if class_obj is None:
        raise exceptions.NotExists()
    return class_obj


async def get_classes(
    db: AsyncSession,
    user_uuid: int,
    page: int,
    size: int,
    status: str,
    search: str,
    order_by: str,
    order: str,
    user_role: str,
):
    stmt = select(ClassModel)
    if user_role != "admin":
        class_member_list = await get_class_member_by_uuid(db, user_uuid=user_uuid)
        if not class_member_list:
            raise exceptions.InvalidParameter()
        class_uuids = [member.class_uuid for member in class_member_list]
        stmt = stmt.where(ClassModel.class_uuid.in_(class_uuids))
    # 偏移量
    offset = (page - 1) * size
    if status:
        stmt = stmt.where(ClassModel.status == status)
    if search:
        stmt = stmt.where(
            or_(
                ClassModel.class_uuid.ilike(f"%{search}%"),
                ClassModel.class_name.ilike(f"%{search}%"),
                ClassModel.teacher_uuid.ilike(f"%{search}%"),
                ClassModel.invite_code.ilike(f"%{search}%"),
            )
        )
    # 排序字段和方向
    order_column = getattr(ClassModel, order_by, None)
    if order_column is not None:
        stmt = stmt.order_by(
            desc(order_column) if order == "desc" else asc(order_column)
        )

    # 分页
    stmt = stmt.offset(offset).limit(size)
    # 查询数据
    result = await db.execute(stmt)
    items = result.scalars().all()
    # 总数查询（用于分页）
    count_stmt = select(func.count()).select_from(ClassModel)
    if user_role != "admin":
        count_stmt = count_stmt.where(ClassModel.class_uuid.in_(class_uuids))
    if status:
        count_stmt = count_stmt.where(ClassModel.status == status)
    if search:
        count_stmt = count_stmt.where(
            or_(
                ClassModel.class_uuid.ilike(f"%{search}%"),
                ClassModel.class_name.ilike(f"%{search}%"),
                ClassModel.teacher_uuid.ilike(f"%{search}%"),
                ClassModel.invite_code.ilike(f"%{search}%"),
            )
        )
    total = (await db.execute(count_stmt)).scalar_one()
    return items, total


async def submit_assignment(
    db: AsyncSession,
    user_uuid: str,
    class_uuid: str,
    assignment_uuid: str,
    content: str,
    attachments: list[Attachment] | None = None,
):
    """
    提交作业到数据库。

    主要流程：
    1. 校验作业是否存在，并检查用户是否属于班级（无权限将抛出异常）。
    2. 处理附件列表，将 Pydantic Attachment 对象序列化为 JSON 字符串，HttpUrl 转为 str。
    3. 构建 AssignmentSubmissionModel 对象并添加到数据库。
    4. 提交事务并刷新对象，返回新提交记录。
    5. 捕获 IntegrityError 处理重复提交，捕获其他异常记录日志并抛 InvalidParameter。

    参数：
        db (AsyncSession): 异步数据库会话。
        user_uuid (str): 提交作业的用户 UUID。
        class_uuid (str): 作业所属班级 UUID。
        assignment_uuid (str): 作业 UUID。
        content (str): 作业内容。
        attachments (list[Attachment] | None): 附件列表，可为空。

    返回：
        AssignmentSubmissionModel: 成功提交的作业记录。

    异常：
        - AlreadyExists: 用户重复提交作业时抛出。
        - InvalidParameter: 数据库写入失败或参数非法时抛出。
    """
    await get_assignment(db, assignment_uuid, class_uuid, user_uuid)
    if attachments:
        attachments_json = json.dumps(
            (
                [
                    {**a.model_dump(), "url": str(a.url)}  # 关键：转成 str
                    for a in attachments
                ]
                if attachments
                else []
            ),
            separators=(",", ":"),
            ensure_ascii=False,
        )
    else:
        attachments_json = "[]"

    new_assignment = AssignmentSubmissionModel(
        user_uuid=user_uuid,
        assignment_uuid=assignment_uuid,
        content=content,
        attachments=attachments_json,
    )
    try:
        logger.info(
            "尝试添加提交的新作业到数据库: 新提交的作业UUID: %s", assignment_uuid
        )
        db.add(new_assignment)
        await db.commit()
        await db.refresh(new_assignment)
        return new_assignment
    except IntegrityError as e:
        await db.rollback()
        if "UNIQUE constraint failed" in str(e.orig):
            raise exceptions.AlreadyExists()
    except Exception as e:
        logger.error("添加新提交的作业到数据库失败, 错误: %s", e)
        raise exceptions.InvalidParameter()
