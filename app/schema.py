from pydantic import AliasChoices, BaseModel, Field
from datetime import datetime

class UserProfile(BaseModel):
    username: str
    model_config = {'from_attributes': True}

class UserCreate(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)

class UserToken(BaseModel):
    access_token: str
    token_type: str = "bearer"

class Dream(BaseModel):
    id: int
    description: str
    author: str = Field(
        ..., validation_alias=AliasChoices('author_id', 'author'), serialization_alias='author'
    )
    created_at: datetime 
    
    model_config = {'from_attributes': True}

class DreamCreate(BaseModel):
    description: str = Field(..., min_length=1)

class DreamUpdate(BaseModel):
    description: str = Field(..., min_length=1)

class MultipleDreams(BaseModel):
    dreams: list[Dream]
    total_count: int