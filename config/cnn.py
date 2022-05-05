# -*- coding: utf-8 -*-
from os import name
import sys
sys.path.append('../')  # noqa E402
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer as OAuth2
import json

__author__ = "Téllez López Angel"
__copyright__ = "@ROBINA, Oct 2021"
__credits__ = ["Téllez López Angel"]
__license__ = "GPL"
__version__ = "1.0"
__email__ = "atellezl@outlook.com"
__status__ = "Production"


def get_settings():
    # with open('../config/config_dev.json', 'r') as file_config:
    with open('../config/config.json', 'r') as file_config:
        settings = json.load(file_config)
    return settings


settings = get_settings()


class CnnMongo():
    def __init__(self, name_cnn='cnn_auth',
                 db_name='admin_apis',
                 verbose=True):

        self.verbose = verbose
        self.user = settings[name_cnn]['user']
        self.pwd = settings[name_cnn]['pwd']
        self.host = settings[name_cnn]['host']
        self.port = settings[name_cnn]['port']
        self.auth = settings[name_cnn]['auth']
        self.timeout = settings[name_cnn]['timeout']
        self.atlas = settings[name_cnn]['atlas']
        self.new_client = None
        self.__connect()
        self.db_security = self.new_client[db_name]

    def __connect(self):
        try:
            self.new_client = MongoClient(
                'mongodb://{0}:{1}@{2}:{3}/{4}'.format(
                    self.user,
                    self.pwd,
                    self.host,
                    self.port,
                    self.auth
                ),
                serverSelectionTimeoutMS=self.timeout
            )
            info = self.new_client.server_info()
            if self.verbose:
                print('::: [+] User {0} connected! access to db:'.format(
                    self.user), self.new_client.list_database_names())
        except OperationFailure as e:
            if self.verbose:
                print('::: [+] Database authentication failed!')
        except ConnectionFailure as e:
            if self.verbose:
                print('::: [+] Database connection error!, no server found.')


class AuthConfig():
    def __init__(self, cnn_scopes, cnn_apps):
        self.app_code = settings['app_code']
        self.app_name = ''
        self.app_version = ''
        self.app_logo = ''
        self.app_description = ''
        self.app_server_dev = ''
        self.app_server_prod = ''
        # to get a string for SECRET_KEY run: openssl rand -hex 32
        self.SECRET_KEY = ''
        self.ALGORITHM = ''
        self.ATEM = 1
        self.PWD_CONTEXT = CryptContext(schemes=['bcrypt'], deprecated='auto')
        self.SCOPES = {}
        self.SECURITY_SCOPES = self.__getScopes(cnn_scopes=cnn_scopes)
        self.OAUTH2_SCHEME = \
            OAuth2(tokenUrl='/auth/login/token', scopes=self.SCOPES)
        # Variables de configuración de CORS
        self.cors_origins = []
        self.cors_origin_regex = ""
        self.cors_credentials = False
        self.cors_methods = []
        self.cors_headers = []
        self.cors_max_age = 60
        self.__getApp(cnn_apps=cnn_apps)

    def __getScopes(self, cnn_scopes):
        scopes = cnn_scopes.find({'app_code': self.app_code})
        scopes_list = []
        if scopes:
            for scope in scopes:
                self.SCOPES[scope.get('name')] = scope.get('description')
                scopes_list.append(scope.get('name'))
        return scopes_list

    def __getApp(self, cnn_apps):
        app = cnn_apps.find_one({'code': self.app_code})

        if app:
            self.app_name = app.get('name', '')
            self.app_version = app.get('version', '')
            self.app_logo = app.get('logo', '')
            self.app_description = app.get('description', '')
            self.app_server_dev = app.get('server_dev', '')
            self.app_server_prod = app.get('server_prod', '')
            app_security = app.get('security', {})

            if app_security:
                self.SECRET_KEY = app_security.get('secret_key', '')
                self.ALGORITHM = app_security.get('algorithm', '')
                self.ATEM = int(app_security.get('time_expire_in_minutes', 0))

            # Variables para manejo de CORS
            app_cors = app.get('cors', {})
            if app_cors:
                self.cors_origins = app_cors.get('origins', [])
                self.cors_expose_headers = app_cors.get('expose_headers', [])
                self.cors_credentials = \
                    app_cors.get('allow_credentials', False)
                self.cors_methods = app_cors.get('allow_methods', [])
                self.cors_headers = app_cors.get('allow_headers', [])
                self.cors_origin_regex = app_cors.get('allow_origin_regex', '')
                self.cors_max_age = int(app_cors.get('max_age', 60))


"""
    Realizamos todas las conexiones y obtenemos las configuraciones de la BD.
"""
# dbSecurity = CnnMongo(db_name='apis_robina')
dbSecurity = CnnMongo()
dbUsers = dbSecurity.db_security['users']
dbApps = dbSecurity.db_security['apps']
dbServices = dbSecurity.db_security['services']
dbScopes = dbSecurity.db_security['scopes']

AUTH_CONFIG = AuthConfig(cnn_scopes=dbScopes, cnn_apps=dbApps)
