#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/8/20 10:41
# @Author  : v_shxliu
# @File    : x-sign.py

import hashlib


def generate_x_sign(api):
    x_sign = "X"
    m = hashlib.md5()
    m.update((api + "WSUDD").encode())
    return x_sign + m.hexdigest()


if __name__ == '__main__':
    sign = generate_x_sign('/fe_api/burdock/weixin/v2/user/5be7cc113f7fe70001cfca01/notes?page=1&page_size=15')
    print(sign)
