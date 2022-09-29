"""PATH OPERATION For Articles - ROUTE"""

from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter, Path
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, schemas, utils, oauth2
from ..database import get_db


router = APIRouter(
	prefix="/articles",
	tags=["Articles"],
	)


@router.get("/", response_model=list[schemas.ArticleOut], summary="Get Current User Articles")
def get_articles(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    articles = db.query(models.Article).filter(models.Article.owner_id == current_user.id).all()
    return articles


@router.get("/{id}", response_model=schemas.ArticleOut)
def get_article(id: int = Path(..., gt=0), db: Session = Depends(get_db), 
	current_user: int = Depends(oauth2.get_current_user)):
	article = db.query(models.Article).filter(models.Article.id == id).first()
	if article is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
							detail=f"article with id: {id} was NOT FOUND")
	if article.owner_id != current_user.id:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
							detail=f"UNAUTHORIZED ACTION")
	return article


@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(id: int = Path(..., gt=0), db: Session = Depends(get_db), 
	current_user: int = Depends(oauth2.get_current_user)):
    
    post_query = db.query(models.Article).filter(models.Article.id == id) # object
    post_to_delete = post_query.first()

    if post_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"article with id: {id} was NOT FOUND")
    if post_to_delete.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"UNAUTHORIZED ACTION")
    post_query.delete(synchronize_session=False) # delete return count of rows matched
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)