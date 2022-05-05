# -*- coding: utf-8 -*-
__author__ = "Oscar López"
__copyright__ = "Copyright 2021, Robina"
__credits__ = ["Oscar López"]
__license__ = "GPL"
__version__ = "2.0.0"
__email__ = "lpz.oscr@gmail.com"
__status__ = "Production"

import sys
import os
sys.path.append('../')  # noqa
import uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
from routes.auth import auth_routes
from routes.credentials import credentials_routes
from config.cnn import AUTH_CONFIG


# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
app = FastAPI()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=AUTH_CONFIG.app_name,
        version=AUTH_CONFIG.app_version,
        description=AUTH_CONFIG.app_description,
        # servers=[
        #     {"url": AUTH_CONFIG.app_server_dev,"description": "Sandbox"},
        #     {"url": AUTH_CONFIG.app_server_prod,"description": "Production"},
        # ],
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {"url": AUTH_CONFIG.app_logo}
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.include_router(auth_routes)
app.include_router(credentials_routes)


app.openapi = custom_openapi


# Add middleware to acept CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=AUTH_CONFIG.cors_origins,
    allow_credentials=AUTH_CONFIG.cors_credentials,
    allow_methods=AUTH_CONFIG.cors_methods,
    allow_headers=AUTH_CONFIG.cors_headers
    # expose_headers=AUTH_CONFIG.cors_expose_headers
)

# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
if __name__ == '__main__':

    uvicorn.run('app:app',
                host='0.0.0.0',
                port=49102,
                reload=True,
                debug=True,
                workers=1)
