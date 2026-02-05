from fastapi import HTTPException

class NotFoundException(HTTPException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(status_code=404, detail=message)

class BadRequestException(HTTPException):
    def __init__(self, message: str = "Bad request"):
        super().__init__(status_code=400, detail=message)

class InternalServerErrorException(HTTPException):
    def __init__(self, message: str = "Internal server error"):
        super().__init__(status_code=500, detail=message)

class UnauthorizedException(HTTPException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(status_code=401, detail=message)

class ForbiddenException(HTTPException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(status_code=403, detail=message)

__all__ = [
    "BadRequestException",
    "ForbiddenException",
    "InternalServerErrorException",
    "NotFoundException",
    "UnauthorizedException",
]