#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/8/30 16:02
# @Author  : v_shxliu
# @File    : downloader.py
import requests
from retry import retry


class Downloader(object):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/84.0.4147.105 Safari/537.36",
        }
        self.cookies = dict()

    def build_request(self, url=None):
        pass

    @retry(tries=3)
    def download(self, url, method, data=None, proxies=None, timeout=(10, 30)):
        if proxies is None:
            proxies = {}
        if data is None:
            data = {}
        self.build_request(url)
        response = requests.request(url=url, method=method, data=data, headers=self.headers, cookies=self.cookies,
                                    proxies=proxies, timeout=timeout)
        return response
