"""PATH OPERATION For User"""

from fastapi import Response, status, HTTPException, Depends, APIRouter, Path
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..database import get_db


router = APIRouter(
	prefix="/users",
	tags=["Users"],
	)


@router.post("/", status_code = status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
	if db.query(models.User).filter(models.User.email == user.email).first(): # if not None -> found a match
	 	raise HTTPException(status_code=422,
	 						detail=f"email: {user.email} already exists")
	user.password = utils.get_hash_password(user.password)
	new_user = models.User(**user.dict())
	db.add(new_user)
	db.commit()
	db.refresh(new_user)
	return new_user


# id should be an integer bigger than 0
@router.get('/{id}', response_model=schemas.UserOut)
def get_user(id: int = Path(..., gt=0), db: Session = Depends(get_db)):
	user = db.query(models.User).filter(models.User.id == id).first()
	if user is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
							detail=f"user with id: {id} was NOT FOUND")
	return user