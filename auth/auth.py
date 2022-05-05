# -*- coding: utf-8 -*-
import sys
sys.path.append('../')  # noqa E402
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordRequestForm, SecurityScopes
from pydantic import ValidationError
from jose import JWTError, jwt
import json
from datetime import datetime, timedelta
from typing import List, Optional
from schemas.user import User, Service, UserInDB, TokenData, Token
from config.cnn import dbUsers, dbServices, AUTH_CONFIG

__author__ = "Téllez López Angel"
__copyright__ = "@ROBINA, Oct 2021"
__credits__ = ["Téllez López Angel"]
__license__ = "GPL"
__version__ = "1.0"
__email__ = "atellezl@outlook.com"
__status__ = "Production"


def get_password_hash(password):
    """
    Hasheamos el password
    """
    return AUTH_CONFIG.PWD_CONTEXT.hash(password)


def verify_password(plain_password, hashed_password):
    """
    Verificamos que el password sea valido
    """
    return AUTH_CONFIG.PWD_CONTEXT.verify(plain_password, hashed_password)


def get_user(username: str):
    """
    Obenemos los datos del usuario de la BD
    """
    user_bd = dbUsers.find_one({'username': username})
    if user_bd is None:
        return None
    return UserInDB(**user_bd)


def authenticate_user(username: str, plain_pwd: str):
    """
        Valida que el usuario exista en nuestra BD
        y verifica que el pwd sea correcto
    """
    user = get_user(username)
    if not user:
        return False

    if not verify_password(plain_pwd, user.password):
        return False

    return user


def create_access_token(data: dict,
                        expires_delta: Optional[timedelta] = None,
                        scopes_from_db=True):
    """
    Generamos el token codificando los datos que se le pasan en el diccionario
    "data" o los que estan definidos en base de datos cuando
    scopes_from_db=True
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=2)

    to_encode.update({'exp': expire})

    # Verificamos que el usuario tenga contratado el servicio.
    service = get_service_scope(username=to_encode.get('sub', ''))

    permihssion_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Not authorized. Service not contracted or inactive.',
        headers={'WWW-Authenticate': 'Servicio no contratado o inactivo.'},
    )

    if not service:
        raise permihssion_exception

    if service.get('disabled', True):
        raise permihssion_exception

    scopes = []
    scopes.append(service.get('scope', ''))
    if scopes_from_db:
        to_encode.update({'scopes': scopes})

    encoded_jwt = jwt.encode(to_encode,
                             AUTH_CONFIG.SECRET_KEY,
                             algorithm=AUTH_CONFIG.ALGORITHM)
    return encoded_jwt


async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(AUTH_CONFIG.OAUTH2_SCHEME)
):
    """
    Obtenemos el usuario actual:
    1. Validamos si se necesitan validar alcances.
    2. DEcodificamos el token.
    3. Verificamos los accesos autorizados mediante los scopes.
    """
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f'Bearer'

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': authenticate_value},
    )

    try:
        payload = jwt.decode(
            token,
            AUTH_CONFIG.SECRET_KEY,
            algorithms=[AUTH_CONFIG.ALGORITHM]
        )
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception

        token_scopes = payload.get('scopes', [])
        token_data = TokenData(scopes=token_scopes, username=username)

    except (JWTError, ValidationError):
        raise credentials_exception

    user_bd = get_user(token_data.username)
    if not user_bd:
        raise credentials_exception

    if user_bd.disabled:
        raise HTTPException(status_code=400, detail='Inactive user')

    permihssion_exception = HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Not enough permihssions',
                            headers={'WWW-Authenticate': authenticate_value},
                            )

    if security_scopes.scopes:
        for scope in token_data.scopes:
            if scope not in security_scopes.scopes:
                raise permihssion_exception
            else:
                break

    return user_bd


async def get_current_active_user(
    current_user: User = Security(
                            get_current_user,
                            scopes=[]
                        )
):
    """
    Verificamos si el usuario esta inactivo, en otro caso devolvemos
    el usuario validado
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail='Inactive user')
    return current_user


def get_service_scope(username):
    """
    1. Obtenemos los datos del servicio asociado al usuario
    """
    service = dbServices.find_one({'username': username,
                                   'app_code': AUTH_CONFIG.app_code})
    return service
