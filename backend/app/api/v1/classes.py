import logging
from typing import Optional, Union

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from core.response import to_response
from core.security import is_admin, is_teacher, is_teacher_or_admin
from db.connector import DatabaseConnector
from schemas import User
from schemas.Request import (
    CreateAssignmentRequest,
    CreateClassRequest,
    JoinClassRequest,
    UpdateClassRequest,
)
from schemas.Response import (
    ApiResponse,
    AssignmentData,
    AssignmentResponse,
    ClassData,
    ErrorResponse,
    PageData,
    Pagination,
)
from services.classes import (
    create_assignment,
    create_class,
    delete_class,
    get_assignment,
    get_assignments,
    get_class,
    join_class,
    update_class,
)

router = APIRouter(prefix="/classes", tags=["Classes"])
logger = logging.getLogger("api.v1.classes")


@router.post("", response_model=Union[ApiResponse, ErrorResponse])
async def create_class_route(
    form_data: CreateClassRequest,
    db: AsyncSession = Depends(DatabaseConnector.get_db),
    _: None = Depends(is_admin),
):
    """
    创建新班级接口

    仅管理员可访问，用于创建新的班级并指定负责教师。

    - 权限：仅限管理员（is_admin）
    - 参数：班级名、描述、教师UUID
    - 返回：创建成功消息
    """
    logger.info(f"创建新班级请求，{form_data.class_name}")
    await create_class(
        db,
        class_name=form_data.class_name,
        description=form_data.description,
        teacher_uuid=form_data.teacher_uuid,
    )
    logger.info(f"创建新班级成功，{form_data.class_name}")
    return to_response(message="Class created successfully")


@router.delete("/{class_uuid}", response_model=Union[ApiResponse, ErrorResponse])
async def delete_class_route(
    class_uuid: str,
    db: AsyncSession = Depends(DatabaseConnector.get_db),
    _: None = Depends(is_teacher_or_admin),
    current_user: User = Depends(get_current_user),
):
    """
    删除指定班级接口

    参数:
    - class_uuid (str): 路径参数，目标班级的 UUID，用于标识要删除的班级。
    - db (AsyncSession): 依赖注入，异步数据库会话，用于执行删除操作。
    - _ (None): 依赖注入，用于权限验证，确保当前用户是教师或管理员。
    - current_user (User): 依赖注入，当前经过身份验证的用户对象。

    权限:
    - 只有拥有教师或管理员权限的用户可以执行删除操作。

    功能:
    - 调用 `delete_class` 函数，传入数据库会话、班级 UUID、当前用户 UUID 和角色，执行班级删除逻辑。
    - 删除班级时，应级联删除该班级相关的作业、班级成员等关联数据（具体由数据库约束和业务逻辑决定）。

    返回:
    - 成功时返回标准成功响应，message 字段提示“Class created successfully”。
    - 失败时返回错误响应。

    注意:
    - 这里返回信息中的“Class created successfully”应修改为删除成功提示，避免语义混淆。
    """
    await delete_class(db, class_uuid, current_user.uuid, current_user.role)
    return to_response(message="Class deleted successfully")


@router.get("/{class_uuid}/homeworks", response_model=Union[ApiResponse, ErrorResponse])
async def get_assignments_route(
    class_uuid: str,
    order_by: str,
    order: str,
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, le=15),
    db: AsyncSession = Depends(DatabaseConnector.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取指定班级的作业列表（支持分页、搜索、筛选和排序）

    参数:
    - class_uuid (str): 路径参数，目标班级的 UUID。
    - status (str): 查询参数，过滤作业的状态（如“已发布”、“草稿”等）。
    - search (str): 查询参数，关键词搜索，用于匹配作业标题或描述。
    - order_by (str): 查询参数，指定排序字段（例如“deadline”、“created_at”等）。
    - order (str): 查询参数，排序顺序，“asc” 或 “desc”。
    - page (int): 查询参数，分页页码，默认1，最小值为1。
    - size (int): 查询参数，每页条数，默认10，最大值为10。
    - db (AsyncSession): 依赖注入，异步数据库会话，用于执行数据库操作。
    - current_user (User): 依赖注入，当前经过身份验证的用户对象。

    返回:
    - ApiResponse: 包含分页后的作业数据列表和分页信息。
    - ErrorResponse: 出错时返回的错误信息结构。

    逻辑流程:
    1. 调用 `get_assignments` 函数，从数据库异步获取符合条件的作业列表及总数。
    2. 根据总数和每页大小计算总页数。
    3. 使用 Pydantic 的 `model_validate` 方法将数据库模型对象转换为响应模型。
    4. 将作业列表和分页信息封装成统一响应结构，返回给客户端。
    """
    items, total = await get_assignments(
        db=db,
        user_uuid=current_user.uuid,
        class_uuid=class_uuid,
        page=page,
        size=size,
        status=status,
        search=search,
        order_by=order_by,
        order=order,
    )

    pages = (total + size - 1) // size

    return to_response(
        data=PageData(
            items=[AssignmentData.model_validate(item) for item in items],
            pagination=Pagination(page=page, size=size, total=total, pages=pages),
        )
    )


@router.post(
    "/{class_uuid}/homeworks", response_model=Union[ApiResponse, ErrorResponse]
)
async def create_assignment_route(
    form_data: CreateAssignmentRequest,
    class_uuid: str,
    db: AsyncSession = Depends(DatabaseConnector.get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(is_teacher),
):
    """
    创建作业接口

    教师用户在指定班级下创建新的作业。

    - 权限：教师（is_teacher）
    - 参数：作业标题、描述、内容、截止时间、是否允许迟交、最大分数、附件
    - 返回：创建成功消息
    """
    logger.info(f"创建新作业请求，{form_data.title}")
    await create_assignment(
        db,
        class_uuid=class_uuid,
        title=form_data.title,
        description=form_data.description,
        content=form_data.content,
        status=form_data.status,
        deadline=form_data.deadline,
        max_score=form_data.max_score,
        allow_late_submission=form_data.allow_late_submission,
        attachments=form_data.attachments,
        created_by=current_user.username,
    )
    logger.info(f"创建新作业成功，{form_data.title}")
    return to_response(message="Assignment created successfully")


@router.get(
    "/{class_uuid}/homeworks/{assignment_uuid}",
    response_model=Union[AssignmentResponse, ErrorResponse],
)
async def get_assignment_route(
    assignment_uuid: str,
    class_uuid: str,
    db: AsyncSession = Depends(DatabaseConnector.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    查询作业详情接口

    当前用户在指定班级中查询指定作业的详细信息。

    - 权限：班级成员（已通过 get_class_member_by_uuid 验证）
    - 参数：
        - class_uuid：班级唯一标识符
        - assignment_uuid：作业唯一标识符
    - 返回：作业详情（包含标题、内容、截止时间、附件等信息）
    """

    assignment = await get_assignment(
        db, assignment_uuid, class_uuid, current_user.uuid
    )
    logger.info(
        f"请求结束 - 查询作业成功: class_uuid: {class_uuid}, assignment_uuid: {assignment_uuid}, user_uuid: {current_user.uuid}"
    )
    return to_response(data=AssignmentData.model_validate(assignment))


@router.post("/students", response_model=Union[ApiResponse, ErrorResponse])
async def join_class_route(
    form_data: JoinClassRequest,
    db: AsyncSession = Depends(
        DatabaseConnector.get_db,
    ),
    current_user: User = Depends(get_current_user),
):
    """
    学生加入班级接口

    当前登录用户通过邀请码加入指定班级。

    - 权限要求：当前用户必须为学生（逻辑上校验）
    - 参数：
        - invite_code：班级的邀请码
    - 返回：
        - 当前用户在该班级中的角色信息及加入时间
    """
    joined_class = await join_class(db, form_data.invite_code, current_user)

    logger.info(
        "请求结束 - 加入班级成功: class_uuid=%s, user_uuid=%s",
        joined_class.class_uuid,
        joined_class.profile_name,
    )

    return to_response(data=joined_class)


@router.put("/{class_uuid}", response_model=Union[ApiResponse, ErrorResponse])
async def update_class_route(
    class_uuid: str,
    form_data: UpdateClassRequest,
    db: AsyncSession = Depends(
        DatabaseConnector.get_db,
    ),
    current_user: User = Depends(get_current_user),
    _: None = Depends(is_teacher_or_admin),
):
    """
    更新指定班级的信息，仅限管理员或教师角色访问。

    接口路径：
        PUT /{class_uuid}

    功能描述：
    1. 校验当前用户是否具备管理员或教师权限（依赖注入方式）。
    2. 获取请求体中的班级名称和描述字段。
    3. 调用服务层函数执行更新操作，包括权限校验、数据落库和异常处理。
    4. 成功后返回统一的成功响应，失败时由全局异常处理器捕获并响应。

    路径参数：
        class_uuid (str): 要更新的班级唯一标识符。

    请求体：
        form_data (UpdateClassRequest):
            - class_name (str): 新的班级名称。
            - description (str): 新的班级描述。

    权限依赖：
        - 当前用户必须为教师或管理员（通过 is_teacher_or_admin 依赖注入）。

    响应：
        - 成功：返回 ApiResponse，message 为 "success"
        - 失败：返回 ErrorResponse，由异常处理器捕捉抛出

    异常：
        - AlreadyExists: 如果班级名称已存在。
        - NotFoundException: 班级不存在或用户不具备班级成员身份。
        - InvalidParameter: 非法请求参数或其他更新异常。
    """
    class_obj = await update_class(
        db,
        class_uuid,
        form_data.class_name,
        form_data.description,
        current_user.uuid,
        current_user.role,
    )

    logger.info("请求结束 - 更新班级信息班级成功: class_uuid=%s", class_uuid)
    return to_response(data=ClassData.model_validate(class_obj))


@router.get("/{class_uuid}", response_model=Union[ApiResponse, ErrorResponse])
async def get_class_route(
    class_uuid: str,
    db: AsyncSession = Depends(
        DatabaseConnector.get_db,
    ),
    _: None = Depends(is_teacher_or_admin),
    current_user: User = Depends(get_current_user),
):
    """
    根据班级UUID获取单个班级信息。

    主要流程：
    1. 通过路径参数 {class_uuid} 接收班级唯一标识符。
    2. 使用 `Depends(is_teacher_or_admin)` 确保只有教师或管理员角色能访问此路由。
    3. 获取当前登录的用户信息，以便进行后续的权限校验。
    4. 调用 `get_class` 业务逻辑函数，传入数据库会话、班级UUID和当前用户信息。
       - **注意：这里需要传入 `current_user.user_uuid` 参数，以确保 `get_class` 函数能够正确校验权限。**
    5. 将获取到的班级对象 `class_obj` 传递给 `ClassData.model_validate` 进行数据验证和模型转换。
    6. 使用 `to_response` 函数封装最终的响应数据，返回给客户端。

    参数：
        class_uuid (str): 班级的唯一标识符。
        db (AsyncSession): 数据库异步会话。
        current_user (User): 当前认证的用户对象。

    返回：
        ApiResponse: 包含班级数据的成功响应。
        ErrorResponse: 如果发生错误（如班级不存在、权限不足等）则返回错误响应。
    """
    class_obj = await get_class(db, class_uuid, current_user.role)
    return to_response(data=ClassData.model_validate(class_obj))


# TO-DO
async def get_classes_route():
    pass
