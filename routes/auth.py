# -*- coding: utf-8 -*-
from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from auth.auth import *


__author__ = "Téllez López Angel"
__copyright__ = "@ROBINA, Oct 2021"
__credits__ = ["Téllez López Angel"]
__license__ = "GPL"
__version__ = "1.0"
__email__ = "atellezl@outlook.com"
__status__ = "Production"


auth_routes = APIRouter(prefix="/auth", tags=["Authentication"])


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
@auth_routes.post('/login/token', response_model=Token)
async def get_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user_db = authenticate_user(form_data.username, form_data.password)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires = timedelta(minutes=AUTH_CONFIG.ATEM)
    access_token = create_access_token(
        data={
            'sub': user_db.username,
            "scopes": form_data.scopes
        },
        expires_delta=access_token_expires
    )
    return {
        'access_token': access_token,
        'token_type': 'bearer'
    }


@auth_routes.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """test"""
    return current_user
