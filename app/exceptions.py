from fastapi import Request, status
from fastapi.responses import JSONResponse


class BusinessRuleError(Exception):
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


async def business_rule_handler(request: Request, exc: BusinessRuleError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.detail},
    )


async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )