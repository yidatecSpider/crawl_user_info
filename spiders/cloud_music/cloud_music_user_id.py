#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/8/26 15:23
# @Author  : v_shxliu
# @File    : cloud_music.py
import json
from time import sleep

import requests
from lxml import etree

from common.downloader import Downloader
from common.params import Params

singer_type_list = [
    '1001',
    '1002',
    '1003'
]


def get_art_list(url):
    print("请求url:{}".format(url))
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/"
                      "92.0.4515.131 Safari/537.36",
        "authority": "music.163.com",
        "upgrade-insecure-requests": "1",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
                  "application/signed-exchange;v=b3;q=0.9",
    }
    res = requests.get(url, headers=headers)
    res.encoding = 'utf-8'
    page = etree.HTML(res.content.decode(), parser=etree.HTMLParser(encoding='utf-8', collect_ids=False))
    art_item_list = page.xpath('//ul[@id="m-artist-box"]//a[@class="nm nm-icn f-thide s-fc0" or @class=""]/@href')
    if not art_item_list:
        raise Exception("请求失败")
    return set([art_uri[art_uri.rfind('=') + 1:] for art_uri in art_item_list])


class SearchUserId(object):
    def __init__(self):
        self.downloader = Downloader()
        self.params = Params()
        self.api_data = dict()
        self.search_api = "https://music.163.com/weapi/cloudsearch/get/web"

    def request_api(self, url, params):
        self.params.generate_params(params)
        data = {
            "params": self.params.params,
            "encSecKey": self.params.sec_key
        }
        return self.downloader.download(url, "POST", data)

    def parse_singer_id(self, query, offset, limit):
        post_data = {
            "hlpretag": "<span class=\"s-fc7\">",
            "hlposttag": "</span>",
            "#/msg/m/private": "",
            "s": query,
            "type": "100",
            "offset": offset,
            "total": "true",
            "limit": limit,
            "csrf_token": "1b3c8812f572e7836e8048031fa51fbf"
        }
        res = self.request_api(self.search_api, post_data)
        json_data = json.loads(res.content)['result']
        total_size = json_data['artistCount']
        try:
            artists = [artist['id'] for artist in json_data['artists']]
        except KeyError:
            print(json_data)
            return
        self.api_data['singer'] += artists
        if len(self.api_data['singer']) < total_size:
            offset = int(offset)
            offset += 90
            self.parse_singer_id(query, str(offset), limit)
        else:
            with open("../search_user_id.txt", 'a+') as wfp:
                for user_id in self.api_data['singer']:
                    wfp.write(str(user_id) + '\n')

    def parse_user_id(self, query, offset, limit):
        post_data = {
            "hlpretag": "<span class=\"s-fc7\">",
            "hlposttag": "</span>",
            "#/msg/m/private": "",
            "s": query,
            "type": "1002",
            "offset": "0",
            "total": offset,
            "limit": limit,
            "csrf_token": "1b3c8812f572e7836e8048031fa51fbf"
        }

        res = self.request_api(self.search_api, post_data)
        json_data = json.loads(res.content)['result']
        total_size = json_data['userprofileCount']
        artists = [artist['userId'] for artist in json_data['userprofiles']]
        self.api_data['user'] += artists
        if len(self.api_data['user']) < total_size:
            offset = int(offset)
            offset += 100
            self.parse_user_id(query, str(offset), limit)
        else:
            with open("../search_user_id.txt", 'a+') as wfp:
                for user_id in self.api_data['user']:
                    wfp.write(str(user_id) + '\n')

    def parse(self, query):
        self.api_data['singer'] = list()
        self.api_data['user'] = list()
        self.parse_singer_id(query, "0", "90")
        # self.parse_user_id(query, "0", "100")
        pass


if __name__ == '__main__':
    queries = ["原创音乐", "音乐人", "作词", "作曲", "词曲改编", "乐队", "好声音"]
    search = SearchUserId()
    for query in queries:
        print("搜索:%s" % query)
        search.parse(query)
    # art_id_list = list()
    # list_url = [
    #     'https://music.163.com/discover/artist/cat?id=1001',
    #     'https://music.163.com/discover/artist/cat?id=1001&initial=0',
    #     'https://music.163.com/discover/artist/cat?id=1002',
    #     'https://music.163.com/discover/artist/cat?id=1002&initial=0',
    #     'https://music.163.com/discover/artist/cat?id=1003',
    #     'https://music.163.com/discover/artist/cat?id=1003&initial=0',
    # ]
    # for singer_type in singer_type_list:
    #     for initial in range(65, 91):
    #         list_url.append('https://music.163.com/discover/artist/cat?id={}&initial={}'.format(singer_type, initial))
    # for url in list_url:
    #     art_id_list += get_art_list(url)
    #     sleep(0.5)
    # with open('../user_id.text', 'w+') as fp:
    #     fp.write('\n'.join(set(art_id_list)))
