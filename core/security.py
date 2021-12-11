#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from starlette.status import HTTP_401_UNAUTHORIZED
from config import config
from auth import users
from util import log


'''config'''
cfg = config.app_config

'''logging'''
log = log.Logger(level=cfg['Application_Config'].app_log_level)

'''oauth2 and jwt'''


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = None


class User(BaseModel):
    username: str
    role: str = None
    full_name: str = None
    email: str = None
    disabled: bool = None


class UserInDB(User):
    hashed_password: str


prefix = cfg['Application_Config'].app_prefix
if prefix.startswith('/'):
    pass
else:
    prefix = '/' + prefix

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=prefix+"/token")


def verify_password(plain_password, hashed_password):
    log.logger.debug('verify_password with hashed_password: [%s]' % hashed_password)
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    log.logger.debug('authenticate_user with username: [%s] and password: [%s]' % (username, password))
    user = get_user(fake_db, username)
    if not user:
        return False
    if user.disabled:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, cfg['Security_Config'].security_key, algorithm=cfg['Security_Config'].security_algorithm)
    log.logger.debug('create_access_token with encoded_jwt: [%s]' % encoded_jwt)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, cfg['Security_Config'].security_key, algorithms=[cfg['Security_Config'].security_algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except PyJWTError:
        raise credentials_exception
    user = get_user(users.Users().users, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_write_permission(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    else:
        if current_user.role.strip() == 'Superadmin' or current_user.role.strip() == 'Writer':
            return True
        else:
            raise HTTPException(status_code=400, detail="Permission denied")


async def get_super_permission(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    else:
        if current_user.role.strip() == 'Superadmin':
            return True
        else:
            raise HTTPException(status_code=400, detail="Permission denied")

if __name__ == '__main__':
    pass
