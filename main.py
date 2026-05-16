from fastapi import FastAPI

from app.api.api_auth import auth_router
from app.api.api_dreams import dreams_router

app = FastAPI(title='Dreams API')

app.include_router(auth_router)
app.include_router(dreams_router)