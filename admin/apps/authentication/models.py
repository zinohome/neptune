# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin

from admin.apps import login_manager

from util.restclient import NeptuneClient


class Users( UserMixin):

    __tablename__ = 'users'

    def __init__(self, username):
        self._username = username
        self._password = None
        self.id = username
        self._is_active = False
        self._is_authenticated = False
        self._is_anonymous = False


    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, value):
        self._is_active = value

    @property
    def is_authenticated(self):
        return self._is_authenticated

    @is_authenticated.setter
    def is_authenticated(self, value):
        self._is_authenticated = value

    @property
    def is_anonymous(self):
        return self._is_anonymous

    @is_anonymous.setter
    def is_anonymous(self, value):
        self._is_anonymous = value

    def __repr__(self):
        return str(self.username)

    def get_id(self):
        return self._username

    def user_login(self):
        nc = NeptuneClient(self.username, self.password)
        logined = nc.user_login()
        if logined:
            self._is_active = True
            self._is_authenticated = True
            self._is_anonymous = False
        return logined

    @staticmethod
    def get(user_id):
        if not user_id:
            return None
        else:
            return Users(user_id)


@login_manager.user_loader
def user_loader(id):
    return Users.get(id)


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    password = request.form.get('password')
    user = Users(username)
    user.password = password
    user.user_login()
    return user
