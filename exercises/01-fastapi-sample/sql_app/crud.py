from sqlalchemy.orm import Session

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
    api_token = _create_unique_token(db)
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password, api_token = api_token)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def _create_unique_token(db: Session):
    while True:
        new_token = token_hex(16)
        # check if the token already exist in database
        if db.query(models.User).filter(models.User.api_token == new_token).first() is None:
            return new_token