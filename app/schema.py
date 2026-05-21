from pydantic import AliasChoices, BaseModel, Field

class UserProfile(BaseModel):
    username: str
    model_config = {'from_attributes': True}

class UserCreate(BaseModel):
    username: str
    password: str

class UserToken(BaseModel):
    access_token: str
    token_type: str = "bearer"

class Dream(BaseModel):
    id: int
    description: str
    author: str = Field(
        ..., validation_alias=AliasChoices('author_id', 'author'), serialization_alias='author'
    )
    model_config = {'from_attributes': True}

class DreamCreate(BaseModel):
    description: str

class DreamUpdate(BaseModel):
    description: str

class MultipleDreams(BaseModel):
    dreams: list[Dream]
    total_count: int
