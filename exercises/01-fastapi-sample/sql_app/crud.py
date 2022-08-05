from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import MultipleResultsFound
from fastapi import HTTPException

from . import models, schemas

from secrets import token_hex

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    api_token = _create_unique_token(db) # Creates an unique token by cheking with DB
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password, api_token = api_token)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Add no owner items (owner_id = 0) to the newly created user
    min_active_userid = db.query(func.min(models.User.id).label("min_user_id")).filter(models.User.is_active == True).one_or_none()[0]
    zero_owner_items = db.query(models.Item).filter(models.Item.owner_id == None).offset(0).limit(100).all() # items with no owner
    if db_user.id == min_active_userid and len(zero_owner_items) > 0: # move no owner items to new user 
        for item in zero_owner_items:
            item.owner_id = db_user.id
    db.commit()
    db_user = get_user(db, db_user.id)

    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_user_item(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Item).filter(models.Item.owner_id == user_id).offset(skip).limit(limit).all()

def delete_user(db: Session, user_id:int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    user.is_active = False
    db.commit()

    items = get_user_item(db, user_id, skip=0, limit=100)
    min_userid = _move_item_min_userid(db, items) # move item to min active user id, if no such user exist, we put 0 (NULL) as user id

    return user
def _create_unique_token(db: Session):
    """
    Helper function to create unique api token
    """
    while True:
        new_token = token_hex(16)
        # check if the token already exist in database
        if db.query(models.User).filter(models.User.api_token == new_token).first() is None:
            return new_token

def _move_item_min_userid(db: Session, items:List[models.Item]):
    """
    Helper function to move items to min active user id, if no such user exist, we put 0 (NULL) as user id
    """
    try:
        min_active_userid = db.query(func.min(models.User.id).label("min_user_id")).filter(models.User.is_active == True).one_or_none()

        if min_active_userid is None:
            min_active_userid = 0
        else:
            min_active_userid = min_active_userid[0]
        for item in items:
            item.owner_id = min_active_userid
        db.commit()
        return min_active_userid

    except MultipleResultsFound:
        raise HTTPException(status_code=500, detail="Multiple User with ID {min_active_userid} found")
     