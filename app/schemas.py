"""pydantic models"""
from fastapi import Query
from pydantic import BaseModel, HttpUrl, EmailStr
from datetime import datetime


###############user schemas###############
class UserBase(BaseModel):
	email: EmailStr

# request
class UserCreate(UserBase):
	password: str = Query(..., min_length=6, max_length=24)

# response
class UserOut(UserBase):
	id: int
	created_at: datetime

	class Config:
		orm_mode = True

class UserLogin(UserBase):
	password: str
###############article schemas###############
class ArticleBase(BaseModel):
	url: HttpUrl


class ArticleCreate(ArticleBase):
	pass


class ParsedArticle(BaseModel):
	title: str
	author: str | None = None
	subject: str | None = None
	content: str


class PredictionRes(BaseModel):
	label: str
	confidence: float


class ArticleOut(ArticleBase ,ParsedArticle, PredictionRes):
	id: int
	owner_id: int

	class Config:
		orm_mode = True


class Token(BaseModel):
	access_token: str
	token_type: str


class TokenData(BaseModel):
	id: str | None = None