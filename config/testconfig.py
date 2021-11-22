#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from unipath import Path
from decouple import config

BASE_DIR = Path(__file__).parent.parent
print(BASE_DIR)
config.encoding = 'utf-8'
config.search_path = BASE_DIR
SECRET_KEY = config('SECRET_KEY', default='bgt56yh@Passw0rd')
SECRET_KEY = config('security_key', default='bgt56yh@Passw0rd')
DEBUG = config('DEBUG', default=False, cast=bool)



if __name__ == '__main__':
    print(config('SECRET_KEY'))
    print(config('security_key'))
    print(config('DEBUG'))