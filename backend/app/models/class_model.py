from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
    ForeignKey,
)
from db.connector import Base
from utils import random
from sqlalchemy.orm import relationship


class ClassModel(Base):
    __tablename__ = "classes"

    class_uuid = Column(
        String(36),
        primary_key=True,
        default=lambda: str(random.generate_uuid()),
        comment="班级 UUID",
    )
    class_name = Column(String(100), nullable=False, unique=True, comment="班级名称")
    description = Column(Text, nullable=True, comment="班级描述")
    teacher_uuid = Column(
        String(36), ForeignKey("users.uuid"), nullable=False, comment="教师 UUID"
    )
    invite_code = Column(String(6), primary_key=True)

    assignments = relationship(
        "AssignmentModel",
        back_populates="class_",
        cascade="all, delete-orphan",
    )
    members = relationship(
        "ClassMemberModel",
        back_populates="class_",
        cascade="all, delete-orphan",
    )


class AssignmentModel(Base):
    __tablename__ = "assignments"

    uuid = Column(
        String(36),
        primary_key=True,
        default=lambda: str(random.generate_uuid()),
        comment="作业 UUID",
    )

    class_uuid = Column(
        String(36),
        ForeignKey("classes.class_uuid", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="班级 UUID",
    )

    title = Column(String(100), nullable=False, comment="作业标题")
    description = Column(Text, nullable=True, comment="作业描述")
    content = Column(Text, nullable=True, comment="作业正文")
    status = Column(String(50), nullable=False, comment="作业状态")
    deadline = Column(DateTime, nullable=False, comment="截止时间")
    max_score = Column(Integer, nullable=False, default=100, comment="满分")
    allow_late_submission = Column(Boolean, default=False, comment="允许迟交")
    attachments = Column(JSON, nullable=True, comment="附件列表（JSON数组）")
    submission_count = Column(Integer, default=0, comment="提交次数")
    updated_at = Column(DateTime, nullable=True, comment="更新时间")
    created_by = Column(String(100), nullable=True, comment="创建者信息")
    created_at = Column(DateTime, nullable=True, comment="创建时间")

    class_ = relationship("ClassModel", back_populates="assignments")
    submissions = relationship(
        "AssignmentSubmissionModel",
        back_populates="assignment",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class ClassMemberModel(Base):
    __tablename__ = "class_members"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    class_uuid = Column(
        String(36),
        ForeignKey("classes.class_uuid", ondelete="CASCADE"),
        nullable=False,
        comment="班级 UUID",
    )
    user_uuid = Column(
        String(36),
        ForeignKey("users.uuid", ondelete="CASCADE"),
        nullable=False,
        comment="用户 UUID",
    )

    role = Column(
        String(20), nullable=False, comment="用户在班级中的角色（如 student / teacher）"
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="创建时间",
    )
    class_ = relationship("ClassModel", back_populates="members")
    user = relationship("User", back_populates="class_members")

class AssignmentSubmissionModel(Base):
    __tablename__ = "assignments_submissions"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    assignment_uuid = Column(
        String(36),
        ForeignKey("assignments.uuid", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="作业提交 UUID",
    )

    user_uuid = Column(
        String(36),
        ForeignKey("users.uuid", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="学生 UUID",
    )

    content = Column(Text, nullable=False, comment="提交内容")
    attachments = Column(JSON, nullable=True, comment="附件列表（JSON数组）")

    assignment = relationship("AssignmentModel", back_populates="submissions")