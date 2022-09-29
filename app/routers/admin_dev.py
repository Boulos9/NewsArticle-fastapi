"""PATH OPERATION For Articles - Admin"""

from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db


router = APIRouter(
	prefix="/admin",
	tags=["Admin"],
	)

"""
	- return all items in database
	- articles returned as a list of ArticleOut schemas
"""
@router.get("/all/articles", response_model=list[schemas.ArticleOut])
def get_all_articles(db: Session = Depends(get_db)):
    return db.query(models.Article).all()


# return all user in database
@router.get("/all/users", response_model=list[schemas.UserOut])
def get_all_user(db: Session = Depends(get_db)):
	return db.query(models.User).all()


# delete all articles in database
@router.delete("/delete/all-articles", status_code=status.HTTP_204_NO_CONTENT)
def delete_all_articles(db: Session = Depends(get_db)):  
	articles_table = db.query(models.Article)
	articles_table.delete(synchronize_session=False)
	db.commit()
	return Response(status_code=status.HTTP_204_NO_CONTENT)