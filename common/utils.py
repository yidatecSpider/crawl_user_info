#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2020-11-25 09:23
# @Author  : shixin.liu
# @File    : utils.py
import os
import re
import sys
import threading
import time
import hashlib
import random
from json.decoder import JSONDecodeError
from threading import Lock

import requests

from common import sign
from common.downloader import Downloader
from common.hashlib_get_id import get_raw_video_id

lock = threading.RLock()

ua_list = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Mobile/12A365 MicroMessenger/5.4.1 NetType/WIF",
    "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Mobile Safari/537.36 MicroMessenger/6.0.0.54_r849063.501 NetType/WIFI"
]
auth_list = [
    'wxmp.8a2c5425-c9a1-449b-ba81-26e4f15c6836',
    # 'wxmp.907545e0-6716-40e2-91e5-cd59b7345bd1'
]
headers = {
    "content-type": "application/json",
    # "referer": "https://servicewechat.com/wxb296433268a1c654/58/page-frame.html",
}


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
    proxies = {'http': a}
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


class RedBookDownloader(Downloader):
    def __init__(self, partition):
        super().__init__()
        self.partition = partition

    @staticmethod
    def get_tunnel_proxy():
        # 隧道域名:端口号
        tunnel = "tps526.kdlapi.com:15818"

        # 用户名密码方式
        username = "t14412240697691"
        password = "i69fhq64"
        proxies = {
            "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel},
            "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel}
        }
        return proxies

    def get_proxy(self):
        with open(f"../config/proxy_{self.partition}", 'r') as fp:
            ip = fp.readline()
            return {'http': ip, 'https': ip}

    def set_proxy(self):
        lock.acquire()
        get_proxy_api = 'http://route.xiongmaodaili.com/xiongmao-web/api/glip?secret=0f1fc2dbaca418943cd6b234da5518d2' \
                        '&orderNo=GL20201113201434Ln043IBh&count=1&isTxt=0&proxyType=1 '
        with open(f"../config/proxy_{self.partition}", 'w') as fp:
            res = self.download(get_proxy_api, 'GET')
            res_data = res.json()
            if res_data.get('code') == '-108':
                print(res_data.get('msg'))
            if res_data.get('code') == '0':
                ip = f"http://{res_data['obj'][0]['ip']}:{res_data['obj'][0]['port']}"
                fp.write(ip)
        lock.release()

    def build_request(self, url=None):
        self.headers['x-sign'] = sign.generate_x_sign(url.replace('http://www.xiaohongshu.com', ''))
        self.headers['User-Agent'] = random.choice(ua_list)
        self.headers['authorization'] = random.choice(auth_list)

    def req_download(self, url, tries=10):
        proxy = self.get_tunnel_proxy()
        # proxy = {}
        try:
            rsp = self.download('http://www.xiaohongshu.com' + url, 'get', '', proxy)
            print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}]请求api:{"http://www.xiaohongshu.com" + url}')
            print(f"sign:{self.headers['x-sign']}")
            print(f"状态码:{rsp.status_code}")
            while rsp.status_code != 200 and rsp.status_code != 423 and rsp.status_code != 406:
                if 500 > rsp.status_code > 400:
                    print(rsp.text)
                if rsp.status_code == 502:
                    rsp = self.req_download(url, tries)
                if rsp.status_code == 403:
                    try:
                        content_json = rsp.json()
                        if isinstance(content_json, dict):
                            break
                    except JSONDecodeError:
                        rsp = self.req_download(url, tries)
                if tries <= 1 and rsp.status_code == 461:
                    print("账号异常")
                    rsp = self.req_download(url, tries - 1)
                if tries >= 1:
                    rsp = self.req_download(url, tries - 1)
                if tries <= 0:
                    rsp = self.req_download(url, tries)
        except requests.exceptions.ProxyError:
            rsp = self.req_download(url, tries)
        except requests.exceptions.Timeout:
            rsp = self.req_download(url, tries)
        time.sleep(0.5)
        return rsp


if __name__ == '__main__':
    a = RedBookDownloader('0')
    print(a.get_proxy())
    a.set_proxy()
    print(a.get_proxy())
