# файл не требует изменений

from fastapi import FastAPI

from app.api import api_auth, api_dreams
from app.config import settings

app = FastAPI(debug=settings.DEBUG, title='InDreams', description='InDreams API')

app.include_router(api_dreams.dreams_router)
app.include_router(api_auth.auth_router)
