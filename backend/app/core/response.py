# core/response.py
from datetime import datetime, timezone

from fastapi.responses import JSONResponse

from schemas.Response import ApiResponse, Meta


def to_response(
    data: dict | None = None,
    message: str = "success",
    status: int = 0,
    status_code: int = 200,
) -> JSONResponse:
    if data is None:
        data = {}
    resp = ApiResponse(
        status=status,
        message=message,
        data=(
            data if isinstance(data, dict) else data.model_dump(mode="json")
        ),  # 非json类型转换为json
        meta=Meta(timestamp=datetime.now(timezone.utc).isoformat()),
    )
    return JSONResponse(status_code=status_code, content=resp.model_dump(by_alias=True))
