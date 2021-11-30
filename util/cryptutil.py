#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: Neptune

import base64
from Crypto.Cipher import AES


def add_to_16(value):
    while len(value) % 16 != 0:
        value += '\0'
    return str.encode(value)

def encrypt(key, text):
    aes = AES.new(add_to_16(key), AES.MODE_ECB)
    encrypt_aes = aes.encrypt(add_to_16(text))
    encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')
    return encrypted_text

def decrypt(key, text):
    aes = AES.new(add_to_16(key), AES.MODE_ECB)
    base64_decrypted = base64.decodebytes(text.encode(encoding='utf-8'))
    decrypted_text = str(aes.decrypt(base64_decrypted), encoding='utf-8').replace('\0', '')
    return decrypted_text

if __name__ == '__main__':
    str1 = "neptune_cache&bgt56yhn"
    print(encrypt('bgt56yh@Passw0rd', str1))
    print(decrypt('bgt56yh@Passw0rd',encrypt('bgt56yh@Passw0rd', str1)))