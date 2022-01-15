#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/8/30 9:48
# @Author  : v_shxliu
# @File    : params.py
from Crypto.Cipher import AES
import base64
import time
import json


class Encrypt:
    def __init__(self, key, iv):
        self.key = key.encode('utf-8')
        self.iv = iv.encode('utf-8')

    # @staticmethod
    def pkcs7padding(self, text):
        """明文使用PKCS7填充 """
        padding_size = len(text.encode('utf-8'))
        padding = 16 - padding_size % 16
        padding_text = chr(padding) * padding
        return text + padding_text

    def aes_encrypt(self, content):
        """ AES加密 """
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        # 处理明文
        content_padding = self.pkcs7padding(content)
        # 加密
        encrypt_bytes = cipher.encrypt(content_padding.encode('utf-8'))
        # 重新编码
        result = str(base64.b64encode(encrypt_bytes), encoding='utf-8')
        return result


class Params(object):
    def __init__(self):
        self.key_1 = "0CoJUm6Qyw8W8jud"
        self.key_2 = "aaaabbbbccccdddd"
        self.iv = "0102030405060708"
        self.encText = None
        self.encSecKey = "814e4abf9c1c6a2af74a7ecca8843f3052626c5c054584352e3fd38a519bd659e687cf1c079e1aac5dd9d491af6" \
                         "b8abf92109862ada93dc7b0ef94a8ee79d557ff2a20512b87ce507e357861366b8542139c67896748852d40861" \
                         "04a8dfc99a2e2e0640b46a4357407b72407b2849b323425c6ed45a0222e69d551a2e59e15b7"

    def generate_params(self, send_data):
        send_data = json.dumps(send_data)
        one_text_e = Encrypt(self.key_1, self.iv)
        two_text = one_text_e.aes_encrypt(send_data)
        two_text_e = Encrypt(self.key_2, self.iv)
        self.encText = two_text_e.aes_encrypt(two_text)

    @property
    def params(self):
        return self.encText

    @property
    def sec_key(self):
        return self.encSecKey


if __name__ == '__main__':
    # one_text = '{"ids":"[1316563155]","level":"standard","encodeType":"aac","csrf_token":""}'
    data = {"artistId": 1039686}  # 固定格式的json
    params = Params()
    params.generate_params(data)
    print(params.params)
    print(params.sec_key)
