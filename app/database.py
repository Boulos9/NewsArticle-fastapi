# """Handling our DB Connection"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import get_settings

settings = get_settings()
SQLALCHEMY_DATABASE_URL = settings.dict()["database_credentials"]

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# session object responsible for talking with the databases
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# class MySuperContextManager:
#     def __init__(self):
#         self.db = DBSession()

#     def __enter__(self):
#         return self.db

#     def __exit__(self, exc_type, exc_value, traceback):
#         self.db.close()


# async def get_db():
#     with MySuperContextManager() as db:
#         yield db