# -*- coding: utf-8 -*-
import sys
from fastapi import APIRouter
sys.path.append('../')  # noqa E402
from auth.auth import *

__author__ = "Oscar López"
__copyright__ = "Copyright 2021, Robina"
__credits__ = ["Oscar López"]
__license__ = "GPL"
__version__ = "2.0.0"
__email__ = "lpz.oscr@gmail.com"
__status__ = "Production"


credentials_routes = APIRouter(prefix="/credentials", tags=["Credentials"])

# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


@credentials_routes.post('/create')
def create_credentials(
    current_user: User = Security(get_current_active_user)
):
    """
    Agrega una o mas credenciales en forma de lista `[`{
    'rfc':'ABC800101ZY1', 'password':'password'}`]` a la cuenta del
    usuario activo.
    """

    return {'result': 'acceso liberado,...'}


if __name__ == '__main__':
    pass
