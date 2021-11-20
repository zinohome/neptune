#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio

from simple_rest_client.api import API
from simple_rest_client.resource import AsyncResource
from config import config
from datetime import datetime, timedelta
from util import log
import simplejson as json

'''config'''
cfg = config.Config()

'''logging'''
log = log.Logger(level=cfg.application['app_log_level'])

class NeptuneClient():
    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._lastlogin = 0
        self._token_expired = True
        self._access_token = None
        self._token_type = 'bearer'
        self._api_root_url = 'http://127.0.0.1:' + str(cfg.application['app_http_port']) + cfg.application['app_prefix'] + '/'
        self._api_client = API(api_root_url = self._api_root_url)


    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def token_expired(self):
        if self._lastlogin == 0:
            self._token_expired = True
        else:
            self._token_expired = datetime.utcnow() - lastlogin > timedelta(minutes=cfg.security['access_token_expire_minutes'] - 1)
        return self._token_expired

    @property
    def access_token(self):
        return self._access_token

    @property
    def api_root_url(self):
        return self._api_root_url

    def renew_token(self):
        api = self._api_client
        api.add_resource(resource_name='token')
        request_body = {"username": self.username,"password": self.password}
        response = api.token.create(body = request_body)
        log.logger.debug(response)
        self._access_token = response.body['access_token']
        self._token_type = response.body['token_type']


if __name__ == '__main__':
    lastlogin = datetime.utcnow() - timedelta(minutes=30)
    log.logger.debug(lastlogin)
    log.logger.debug(datetime.utcnow() - lastlogin > timedelta(minutes=cfg.security['access_token_expire_minutes'] - 1))
    log.logger.debug(timedelta(minutes=15))
    nc = NeptuneClient('admin','admin')
    log.logger.debug(nc.token_expired)
    log.logger.debug(nc.api_root_url)
    nc.renew_token()
