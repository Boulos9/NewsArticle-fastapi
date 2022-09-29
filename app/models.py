from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from .database import Base


class Article(Base):
	__tablename__ = "articles"

	id = Column(Integer, primary_key=True, nullable=False) # psycopg3 null_ok
	title = Column(String, nullable=True)
	content = Column(String, nullable=False)
	author = Column(String, nullable=True) # authors
	url = Column(String, nullable=False)
	subject = Column(String, nullable=True) # category
	created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
	label = Column(String, nullable=False)
	confidence = Column(Float, nullable=False)
	
	owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
	owner = relationship("User") # will fetch the user entry in users table based on the owner_id


class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True, nullable=False)
	email = Column(String, nullable=False, unique=True)
	password = Column(String, nullable=False)
	created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))