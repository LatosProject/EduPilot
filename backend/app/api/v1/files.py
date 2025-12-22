import logging
import os
import uuid
from datetime import datetime
from typing import Union

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.responses import FileResponse

from core.dependencies import get_current_user
from core.response import to_response
from schemas import User
from schemas.Response import ApiResponse, ErrorResponse

router = APIRouter(prefix="/files", tags=["Files"])

logger = logging.getLogger("api.v1.files")

# 文件上传配置
# __file__ = backend/app/api/v1/files.py
# 上传目录: backend/app/uploads
APP_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # backend/app
UPLOAD_DIR = os.path.join(APP_DIR, "uploads")
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {
    # 文档
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".md", ".rtf", ".odt", ".ods", ".odp", ".csv",
    # 图片
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico", ".tiff", ".tif", ".heic", ".heif",
    # 压缩包
    ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",
    # 代码
    ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".scss", ".sass", ".less",
    ".java", ".c", ".cpp", ".h", ".hpp", ".cs", ".go", ".rs", ".rb", ".php",
    ".json", ".xml", ".yaml", ".yml", ".toml", ".ini", ".conf", ".cfg",
    ".sql", ".sh", ".bat", ".ps1", ".vue", ".svelte",
    # 其他媒体
    ".mp3", ".mp4", ".wav", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm", ".m4a", ".flac", ".ogg",
}

# 确保上传目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_file_extension(filename: str) -> str:
    """获取文件扩展名（小写）"""
    return os.path.splitext(filename)[1].lower()


def generate_unique_filename(original_filename: str) -> str:
    """生成唯一文件名，保留原始扩展名"""
    ext = get_file_extension(original_filename)
    unique_id = uuid.uuid4().hex[:12]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{timestamp}_{unique_id}{ext}"


@router.post("/upload", response_model=Union[ApiResponse, ErrorResponse])
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    上传单个文件

    - 文件大小限制：100MB
    - 支持常见文档、图片、压缩包等格式
    - 返回：文件名和访问 URL
    """
    logger.info(f"用户 {current_user.uuid} 开始上传文件: {file.filename}, content_type: {file.content_type}")

    # 检查文件名
    if not file.filename:
        logger.warning(f"用户 {current_user.uuid} 上传文件时未提供文件名")
        raise HTTPException(status_code=400, detail="未提供文件名")

    # 检查文件扩展名
    ext = get_file_extension(file.filename)
    logger.info(f"文件扩展名: {ext}")
    if ext not in ALLOWED_EXTENSIONS:
        logger.warning(f"用户 {current_user.uuid} 尝试上传不支持的文件类型: {ext}")
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {ext}")

    # 读取文件内容并检查大小
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        logger.warning(f"用户 {current_user.uuid} 上传文件超过大小限制: {len(content)} bytes")
        raise HTTPException(status_code=400, detail="文件大小超过 100MB 限制")

    # 生成唯一文件名
    unique_filename = generate_unique_filename(file.filename)
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # 保存文件
    try:
        with open(file_path, "wb") as f:
            f.write(content)
        logger.info(f"用户 {current_user.uuid} 上传文件成功: {unique_filename}")
    except Exception as e:
        logger.error(f"保存文件失败: {e}")
        raise HTTPException(status_code=500, detail="文件保存失败")

    # 返回文件信息
    return to_response(
        data={
            "filename": file.filename,
            "stored_filename": unique_filename,
            "url": f"/api/v1/files/download/{unique_filename}",
            "size": len(content),
        }
    )


@router.get("/download/{filename}", response_class=FileResponse)
async def download_file(filename: str):
    """
    下载文件

    - 通过文件名下载之前上传的文件
    """
    file_path = os.path.join(UPLOAD_DIR, filename)

    # 安全检查：防止路径遍历攻击
    if not os.path.abspath(file_path).startswith(os.path.abspath(UPLOAD_DIR)):
        raise HTTPException(status_code=400, detail="非法文件路径")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream",
    )
