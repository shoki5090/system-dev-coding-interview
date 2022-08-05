from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import MultipleResultsFound
from . import models, schemas
from fastapi import HTTPException

def check_token_exist(db: Session, api_token: str):
    """
    Helper Function  to return True or False if the token is active 
    """
    return get_user_id_by_token(db, api_token) is not None

def get_user_id_by_token(db: Session, api_token: str):
    """
    Return the User id if the API Token is valid (exist AND is active)
    """
    try:
        result = db.query(models.User.id).filter(models.User.api_token == api_token, models.User.is_active == True).one_or_none()
        return  result[0] if result is not None else None
    except MultipleResultsFound:
        # Shouldn't exist but if there are multiple with same user api token
        raise HTTPException(status_code=500, detail="Multiple User with same token found")
    

