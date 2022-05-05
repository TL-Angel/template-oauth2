# -*- coding: utf-8 -*-
from typing import List, Optional
from pydantic import BaseModel, Field


__author__ = "Oscar López"
__copyright__ = "Copyright 2021, Robina"
__credits__ = ["Oscar López"]
__license__ = "GPL"
__version__ = "1.0.0"
__email__ = "lpz.oscr@gmail.com"
__status__ = "Development"


class Scope(BaseModel):
    name: str = Field(
        ...,
        title='Scope Name',
        description='Name of scope.',
        regex="^[A-Z_]{3,20}$"
    )
    description: str = Field(
        ...,
        title='Scope Description',
        description='Description of scope.',
        max_length=150
    )

    class Config:
        schema_extra = {
            "example": {
                "name": "GUEST",
                "description": "Usuario invitado."
            }
        }


class Service(BaseModel):
    username: str = Field(
        ...,
        title='UserName',
        description='Description od user name.',
        regex="^[A-Za-z0-9_@.]{3,50}$"
    )
    app_code: str = Field(
        ...,
        regex="^[A-Z]{2}[0-9]{8}$",
        alias="_id",
        title='AppCode',
        description='Unique identifier of application.'
    )
    scopes: List[Scope] = Field(
        [],
        title='Service Scopes',
        description='Set scopes for this service.'
    )

    class Config:
        schema_extra = {
            "example": {
                "username": "name_user",
                "app_code": "RO00000000",
                "scopes": [
                    {
                        "name": "GUEST",
                        "description": "Usuario invitado"
                    },
                    {
                        "name": "USER",
                        "description": "Usuario con permisos limitados"
                    },
                    {
                        "name": "ADMIN",
                        "description": "Usuario con todos permisos."
                    }
                ]
            }
        }


class User(BaseModel):
    username: str = Field(
        ...,
        title='UserName',
        description='User name to send notifications.',
        regex="^[A-Za-z0-9_@.]{3,50}$"
    )
    password: str = Field(
        ...,
        title='UserPassword',
        description='Specify the login password.'
    )

    class Config:
        schema_extra = {
            "example": {
                "username": "name_user",
                "password": "secret"
            }
        }


class UserInDB(User):
    disabled: bool = Field(
        False,
        title='UserEnabled',
        description='Indicates if the user is enabled.'
    )

    class Config:
        schema_extra = {
            "example": {
                "username": "name_user",
                "password": "secret",
                "disabled": False
            }
        }


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []
