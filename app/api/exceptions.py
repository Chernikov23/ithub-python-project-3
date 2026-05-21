from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

class CredentialsHTTPException(HTTPException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers={"WWW-Authenticate": "Bearer"})

class NotFoundHTTPException(HTTPException):
    def __init__(self, detail: str = "Not Found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class ConflictHTTPException(HTTPException):
    def __init__(self, detail: str = "Conflict"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)

class LoginHTTPException(HTTPException):
    def __init__(self, detail: str = "Incorrect username or password"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

async def http_404_not_found_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=404, content={'message': 'Not Found'})

async def http_403_forbidden_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=403, content={'message': 'Forbidden'})