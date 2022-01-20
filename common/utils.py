#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2020-11-25 09:23
# @Author  : shixin.liu
# @File    : utils.py
import base64
import os
import re
import sys
import time
import hashlib

import requests

from .hashlib_get_id import get_raw_video_id


def get_proxy():
    """
    获取代理地址和Proxy-Authorization校验字符串
    :return:代理地址，校验字符
    """
    _version = sys.version_info
    is_python3 = (_version[0] == 3)

    # 个人中心获取orderno与secret
    orderno = "DT20201113204811XiawHrD0"
    secret = "0f1fc2dbaca418943cd6b234da5518d2"
    ip = "dynamic.xiongmaodaili.com"
    # 按量订单端口
    port = "8088"
    # 按并发订单端口
    # port = "8089"

    ip_port = "http://" + ip + ":" + port

    timestamp = str(int(time.time()))  # 计算时间戳
    txt = "orderno=" + orderno + "," + "secret=" + secret + "," + "timestamp=" + timestamp

    if is_python3:
        txt = txt.encode()

    md5_string = hashlib.md5(txt).hexdigest()  # 计算sign
    sign = md5_string.upper()  # 转换成大写
    auth = "sign=" + sign + "&" + "orderno=" + orderno + "&" + "timestamp=" + timestamp + "&change=true"
    return ip_port, auth


def get_response(url):
    print(url)
    a, b = get_proxy()
    headers = {
        "Proxy-Authorization": b,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
    }
    proxies = {'http':a}
    response = requests.get(url, proxies=proxies, headers=headers)
    # response = requests.get(url, headers=headers)
    return response


def format_content(content):
    if content.startswith('：'):
        content = content[1:]
    return content


def extract_id(chat):
    return int(get_raw_video_id(chat))


def extract_row_status(chat):
    row_status = "1"
    return row_status


def get_image_content(url):
    """
    下载图片文件
    :param url: 图片连接
    :return: 图片格式，图片内容二进制流
    """
    try:
        file_type = re.findall(r'\.[^.\\/:*?"<>|\r\n]+$', url)[0]
        img_binary = get_response(url).content
        print("file_type:{}".format(file_type))
        print("binary:{}".format(img_binary))
        return file_type, img_binary
    except IndexError:
        return None, None


def download_chat_image(raw_id, urls, save_path):
    for index, url in enumerate(urls):
        file_type, img_binary = get_image_content(url)
        file_name = '{raw_id}_{index}{file_type}'.format(raw_id=raw_id, index=index, file_type=file_type)
        if img_binary is None:
            return
        if not os.path.exists('../img/{}'.format(raw_id)):
            os.mkdir('../img/{}'.format(raw_id))

        with open('../img/{raw_id}/{file_name}'.format(raw_id=raw_id, file_name=file_name), 'wb+') as fp:
            fp.write(img_binary)
            fp.close()


def extract_id(chat):
    return int(get_raw_video_id(chat))


def filter_emoji(content, restr=''):
    # 过滤表情
    co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    return co.sub(restr, content)


if __name__ == '__main__':
    download_chat_image('111', [
        'http://tiebapic.baidu.com/forum/w%3D580/sign=b571aebec6c8a786be2a4a065708c9c7/a8e75294d143ad4b417d488495025aafa50f067c.jpg',
        'https://tinypng.com//images/example-orig.png',
        'https://img1.doubanio.com/view/photo/m/public/p2618247457.webp'
    ])
