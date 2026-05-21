from fastapi import FastAPI
from app.api.api_auth import auth_router
from app.api.api_dreams import dreams_router
from app.config import settings

app = FastAPI(
    debug=settings.DEBUG, 
    title='InDreams', 
    description='InDreams API'
)

app.include_router(dreams_router)
app.include_router(auth_router)
