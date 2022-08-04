from sqlalchemy.orm import Session

from . import models


def check_token_exist(db: Session, api_token: str):
    return get_user_by_token(db, api_token) is not None

def get_user_by_token(db: Session, api_token: str):
    return db.query(models.User).filter(models.User.api_token == api_token).first()

