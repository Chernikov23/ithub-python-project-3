from pydantic import AliasChoices, BaseModel, Field


class Dream(BaseModel):
	id: int
	description: str
	author: str = Field(
		..., validation_alias=AliasChoices('author_id', 'author'), serialization_alias='author'
	)
	# Для Pydantic v2+:
	model_config = {'from_attributes': True}
	# Для Pydantic v1:
	# class Config:
	#     orm_mode = True


class DreamCreate(BaseModel):
	description: str


class DreamUpdate(BaseModel):
	description: str


class MultipleDreams(BaseModel):
	dreams: list[Dream]
	total_count: int
