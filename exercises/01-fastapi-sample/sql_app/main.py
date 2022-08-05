from typing import List
from pydantic import Required
from fastapi import Depends, FastAPI, HTTPException, Header
from setuptools import Require
from sqlalchemy.orm import Session

from . import crud, models, schemas, auth
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_session = Depends(get_db)


@app.get("/health-check")
def health_check(db: Session = db_session):
    return {"status": "ok"}


@app.post("/users/", response_model=schemas.UserCreateResponse)
def create_user(user: schemas.UserCreate, db: Session = db_session):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, x_api_token: str = Header(Required), db: Session = db_session):
    #check if api token is valid (exist AND is active)
    _check_api_token(db, api_token=x_api_token)
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, x_api_token: str = Header(Required) , db: Session = db_session):
    _check_api_token(db, api_token=x_api_token)
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, x_api_token: str = Header(Required), db: Session = db_session
):
    _check_api_token(db, api_token=x_api_token)
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, x_api_token: str = Header(Required), db: Session = db_session):
    _check_api_token(db, api_token=x_api_token)
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

@app.get("/me/items/", response_model=List[schemas.Item])
def read_user_items(skip: int = 0, limit: int = 100, x_api_token: str = Header(Required), db: Session = db_session):
    user_id = auth.get_user_id_by_token(db=db, api_token=x_api_token)
    if user_id is not None:
        items = crud.get_user_item(db=db, user_id=user_id, skip=skip, limit=limit)
        return items
    else:
        raise HTTPException(status_code=404, detail="API Token not found or not active")

# Endpoint to delete user by setting is active to False
@app.post("/delete_user/{user_id}", response_model=schemas.User)
def delete_user(user_id:int, x_api_token:str = Header(Required), db: Session = db_session):
    _check_api_token(db, api_token=x_api_token)
    db_user = crud.delete_user(db, user_id=user_id)
    return db_user

def _check_api_token(db: Session, api_token: str):
    """
    Helper function that returns bool if api token is valid (exist AND is active)
    """
    if not auth.check_token_exist(db, api_token=api_token):
        raise HTTPException(status_code=404, detail="API Token not found or not active")
    return True