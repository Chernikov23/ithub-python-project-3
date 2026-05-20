from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


async def http_404_not_found_handler(request: Request, exc: HTTPException) -> JSONResponse:
	return JSONResponse(
		status_code=status.HTTP_404_NOT_FOUND,
		content={'message': 'Not Found'},
	)


async def http_403_forbidden_handler(request: Request, exc: HTTPException) -> JSONResponse:
	return JSONResponse(
		status_code=status.HTTP_403_FORBIDDEN,
		content={'message': 'Forbidden'},
	)
