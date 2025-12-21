# schemas/Response.py
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, StrictInt, StrictStr, field_validator

from schemas.User import User


class Meta(BaseModel):
    timestamp: str = Field(..., alias="timestamp", description="响应时间戳")
    model_config = {"populate_by_name": True}


class Error(BaseModel):
    code: StrictInt = Field(..., description="错误代码")
    details: StrictStr = Field(None, description="错误详情")


class ApiResponse(BaseModel):
    status: StrictInt = Field(..., description="状态码，通常 0 表示成功")
    message: StrictStr = Field(..., description="响应消息")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据，成功时返回")
    meta: Meta = Field(default_factory=lambda: Meta(timestamp=""), description="元数据")


class LoginData(BaseModel):
    expires_in: int
    access_token: str
    user: User


class LoginResponse(ApiResponse):
    data: LoginData


class ErrorResponse(ApiResponse):
    error: Error


class Attachment(BaseModel):
    filename: StrictStr
    url: StrictStr


class AssignmentData(BaseModel):
    uuid: StrictStr = Field(..., description="作业ID")
    title: StrictStr = Field(..., description="作业标题")
    content: Optional[StrictStr] = Field(None, description="作业内容")
    description: Optional[StrictStr] = Field(None, description="作业解释")
    deadline: Optional[datetime] = Field(None, description="截止日期")
    max_score: Optional[StrictInt] = Field(None, description="最高分")
    allow_late_submission: Optional[bool] = Field(False, description="是否允许迟交")
    attachments: Optional[List[Attachment]] = Field(
        default_factory=list, description="附件列表"
    )
    submission_count: Optional[StrictInt] = Field(0, description="提交次数")
    created_by: Optional[StrictStr] = Field(None, description="创建者信息")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    submitted: Optional[bool] = Field(False, description="当前用户是否已提交该作业")
    model_config = {"from_attributes": True}

    @field_validator("attachments", mode="before")
    @classmethod
    def parse_attachments_from_db_string(cls, v: Any) -> List[Dict[str, Any]]:
        """
        在验证 attachments 字段之前，如果它是字符串（来自数据库），
        则尝试将其解析为 Python 列表。
        """
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                parsed_list = json.loads(v)
                return parsed_list
            except json.JSONDecodeError as e:
                import logging

                logger = logging.getLogger("schemas.response")
                logger.warning(f"无法解析 attachments 字段为 JSON 列表: {v}, 错误: {e}")
                return []
        if v is None:
            return []
        return v


class ClassUserData(BaseModel):
    class_uuid: StrictStr = Field(..., description="用户名")
    user_uuid: StrictStr = Field(..., description="用户唯一标识符")
    profile_name: StrictStr = Field(..., description="用户个人资料名称")
    role: StrictStr = Field(..., description="用户角色")
    created_at: Optional[datetime] = Field(None, description="加入时间")
    model_config = {"from_attributes": True}


class AssignmentResponse(ApiResponse):
    data: AssignmentData


class Pagination(BaseModel):
    page: int
    size: int
    total: int
    pages: int


class PageData(BaseModel):
    items: List[Any]
    pagination: Pagination


class ClassData(BaseModel):
    class_uuid: StrictStr = Field(..., description="班级唯一标识符")
    class_name: StrictStr = Field(..., description="班级名称")
    description: Optional[StrictStr] = Field(None, description="班级描述")
    teacher_uuid: StrictStr = Field(..., description="班主任唯一标识符")
    invite_code: StrictStr = Field(..., description="班级邀请码")
    model_config = {"from_attributes": True}


class UpdateUserData(BaseModel):
    username: Optional[StrictStr] = Field(None, description="新的用户名")
    email: Optional[StrictStr] = Field(None, description="新的邮箱")
    profile_name: Optional[StrictStr] = Field(None, description="新的个人资料名称")
    avatar_url: Optional[StrictStr] = Field(None, description="新的头像URL")
    role: Optional[StrictStr] = Field(None, description="新的用户角色")
    status: Optional[StrictStr] = Field(None, description="新的用户状态")

    model_config = {"from_attributes": True}
