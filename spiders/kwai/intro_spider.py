#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/4/17 20:23
# @Author  : shixin.liu
# @File    : intro_spider.py
import json

from spiders.kwai.extractors.user_info_extractor import IntroUserInfoExtractor
from spiders.kwai.tag_spider import KwaiTagSpider


class KwaiIntroSpider(KwaiTagSpider):
    def __init__(self):
        super().__init__()
        self.api = "http://wxmini-api.uyouqu.com/rest/wd/wechatApp/search/user?__NS_sig3=6d7d390a8b450f5c9c303332b1f9f1d2aa541b482c2c2e2e21202339&__NS_sig3_origin=3sCt3iAAAAAAAAAAAAAAAwEQBv2b8ewCRWoKUiAAAABa1Uck2OzFjuwHqPh2n/qSj9QknvaoDgEN0sVDnubK8Q=="
        self.user_extractor = IntroUserInfoExtractor()
        self.tag_list = [
            '短剧'
        ]

    def extract_user_list(self, rsp):
        data_json = json.loads(rsp.content)
        self.user_extractor.process(
            [video.get('user_id') for video in data_json.get('users')])


if __name__ == '__main__':
    KwaiIntroSpider().extract()
