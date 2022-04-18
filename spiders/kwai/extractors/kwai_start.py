"""
快手星芒抓取脚本
"""

# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/4/17 10:03
# @Author  : shixin.liu
# @File    : kwai_start.py
import json
import time

import pymysql
import requests

from spiders.kwai.extractors.user_info_extractor import TopListUserInfoExtractor, HotListUserInfoExtractor


class KwaiStartTopSpider(object):
    """今日最热抓取"""
    name = "TOP50"

    def __init__(self):
        self.rank_list = []
        self.user_extractor = TopListUserInfoExtractor()
        self.rank_id = '3'
        self.conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='pass', db='spider',
                                    charset='utf8mb4')
        self.cur = self.conn.cursor()

        self.api = "http://123.184.153.58/rest/n/tube/rankPageV2?c=a&did=132557A7-C0CA-422D-991F-A02437C1F6F0&keyconfig_state=2&kpn=KUAISHOU&grant_browse_type=AUTHORIZED&deviceBit=0&sw=750&is_background=0&kpf=IPHONE&sys=ios14.3&sh=1334&kcv={}&browseType=4&net=_5&darkMode=false&ver={}&mod=iPhone8%2C1&cold_launch_time_ms={}&isp=&vague=0&egid=DFPF198E40F65BE41BA02C32A7C2E2C811415EBE5B1443968E11086B4FF2B19F&appver={}"
        self.sig = [
            {
                "pcursor": "",
                "sig": "3fd134cd5bb2c73de60a446bed95c01d",
                "appver": "10.2.20.6972",
                "var": "10.2",
                "kcv": "1455",
                "cold_launch_time_ms": "1647786494024"
            },
            {
                "pcursor": "10", "sig": "cfb109daf251a16fa1530cc76ab0f2d6", "appver": "10.2.20.6972", "var": "10.2",
                "kcv": "1455", "cold_launch_time_ms": "1647786494024"
            },
            {
                "pcursor": "20", "sig": "b4963614a2da7b21ce5810c986e2a497", "appver": "10.2.20.6972", "var": "10.2",
                "kcv": "1455", "cold_launch_time_ms": "1647786494024"
            },
            {
                "pcursor": "30", "sig": "28a1ac54c7fcbb2d5f96558c3c479e09", "appver": "10.3.10.7078", "var": "10.3",
                "kcv": "1456", "cold_launch_time_ms": "1650165127873"
            },
            {
                "pcursor": "40", "sig": "2c5f2b7d40ec0e097fe3c8d6a916f621", "appver": "10.3.10.7078", "var": "10.3",
                "kcv": "1456", "cold_launch_time_ms": "1650165127873"
            },
        ]

    def extract_hot(self, rsp) -> None:
        """
        解析TOP50响应数据
        :param rsp_list:响应列表
        """
        rank_json = json.loads(rsp.content)
        for videos in rank_json.get('tubes'):
            rank_info = {
                'video_name': videos.get('name'),
                'rank_update_time': time.strftime('%Y-%m-%d %H:%M:%S',
                                                  time.localtime(rank_json.get('rank', {}).get('updateTime') / 1000)),
                'rank_num': videos.get('rankingInfo', {}).get('rankNum'),
                'rank_name': videos.get('rankingInfo', {}).get('rankInfo').get('rankName'),
                'total_subscribe_count': videos.get('rankingInfo', {}).get('rankInfo').get('totalSubscribeCount'),
                'user_id': videos.get('author', {}).get('user_id')
            }
            self.rank_list.append(rank_info)

    def get_api_response(self, page) -> requests.Response:
        """请求接口"""
        headers = {
            'Host': 'apijs2.gifshow.com',
            'Cookie': 'session_id=2B335E29-6157-40AF-80B0-1B21126F9A4D;c=a;kuaishou.api_st=;language=zh-Hans-CN%3Bq%3D1%2C%20en-CN%3Bq%3D0.9;kpn=KUAISHOU;did=132557A7-C0CA-422D-991F-A02437C1F6F0;client_key=56c3713c;country_code=cn;kuaishou.h5_st=;sw=750;cs=false;kpf=IPHONE;power_mode=0;os=14.3;sys=ios14.3;sh=1334;browseType=4;global_id=DFPF198E40F65BE41BA02C32A7C2E2C811415EBE5B1443968E11086B4FF2B19F;net=_5;darkMode=false;ver=10.2;mod=iPhone8%2C1;token=;isp=;thermal=10000;ud=;weblogger_switch=;__NSWJ=86tjV+Yq1F36X8aCk7v+3py/gZ3ERG4BUogf+cQ9mz28Mn7enl0usw6DOuX5I1BBAAAAAQ==;appver=10.2.20.6972;region_ticket=RT_9DB0D5E94A43437CB2046BDEBEF5388A830A3DF3A2E1AF68D8D1A61F23112D4944C351107',
            'Accept': 'application/json',
            'X-REQUESTID': '164778663591406265',
            'User-Agent': 'kwai-ios',
            'Accept-Language': 'zh-Hans-CN;q=1, en-CN;q=0.9',
            'X-Client-Info': 'model=iPhone8,1;os=iOS;nqe-score=10;network=WIFI;',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        body = {
            "__NS_sig3": "b8a9daea96bf3fe9caf0f3f2e4d35dc162d2dc88ede1eff9",
            "client_key": "56c3713c",
            "country_code": "cn",
            "cs": "false",
            "global_id": "DFPF198E40F65BE41BA02C32A7C2E2C811415EBE5B1443968E11086B4FF2B19F",
            "kuaishou.api_st": "",
            "language": "zh-Hans-CN;q=1, en-CN;q=0.9",
            "power_mode": "0",
            "rankId": self.rank_id,
            "thermal": "10000",
            "token": "",
        }
        sig = self.sig[page - 1]
        if sig.get('pcursor'):
            body['pcursor'] = sig.get('pcursor')
            body['sig'] = sig.get('sig')
        else:
            body['sig'] = sig.get('sig')
        return requests.post(
            self.api.format(sig.get('kcv'), sig.get('var'), sig.get('cold_launch_time_ms'), sig.get('appver')),
            headers=headers, data=body)

    def extract_user_info(self) -> None:
        """
        解析用户信息
        """
        user_list = [rank_item.get('user_id') for rank_item in self.rank_list]
        self.user_extractor.process(user_list)

    def save_rank_data(self) -> None:
        """
        保存榜单数据
        """
        sql = None
        try:
            sql = '''insert into kwai_star_day(`video_name`,`rank_update_time`,`rank_num`,`rank_name`,`total_subscribe_count`,
            `user_id`) VALUES (%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE `video_name` = VALUES(
            `video_name`),`user_id` = VALUES(`user_id`),`total_subscribe_count` = VALUES(`total_subscribe_count`),
            `rank_update_time` = VALUES(`rank_update_time`) '''
            self.cur.executemany(sql, [tuple(insert_data.values()) for insert_data in self.rank_list])
            print(f"{self.name}榜单入库成功")
            self.conn.commit()
        except pymysql.err.OperationalError:
            print(sql)
        except pymysql.err.ProgrammingError:
            print(sql)
        except pymysql.err.InterfaceError:
            self.conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='pass', db='spider',
                                        charset='utf8mb4')
            self.cur = self.conn.cursor()

    def extract(self) -> None:
        """
        解析入口
        """
        rsp_list = [self.get_api_response(page) for page in range(5)]
        for rsp in rsp_list:
            self.extract_hot(rsp)
        self.save_rank_data()
        self.extract_user_info()


class KwaiStartHotSpider(KwaiStartTopSpider):
    name = 'Hot'

    def __init__(self):
        super().__init__()
        self.rank_id = '1'
        self.user_extractor = HotListUserInfoExtractor()
        self.api = "http://123.184.153.58/rest/n/tube/rankPageV2?c=a&did=132557A7-C0CA-422D-991F-A02437C1F6F0&kpn=KUAISHOU&grant_browse_type=AUTHORIZED&deviceBit=0&keyconfig_state=2&sw=750&is_background=0&kpf=IPHONE&sys=ios14.3&sh=1334&kcv={}&browseType=4&net=_5&darkMode=false&ver={}&mod=iPhone8%2C1&isp=&cold_launch_time_ms={}&vague=0&egid=DFPF198E40F65BE41BA02C32A7C2E2C811415EBE5B1443968E11086B4FF2B19F&appver={}"
        self.sig = [
            {
                "pcursor": "",
                "sig": "602007090ac98e2c4947d44afc8a1b84",
                "appver": "10.2.20.6972",
                "var": "10.2",
                "kcv": "1455",
                "cold_launch_time_ms": "1647786494024"
            }, {
                "pcursor": "10",
                "sig": "af6b5033d5e7f6d8bfc5177700eca692",
                "appver": "10.2.20.6972",
                "var": "10.2",
                "kcv": "1455",
                "cold_launch_time_ms": "1647787149692"
            }]

    def extract(self) -> None:
        """
        解析入口
        """
        rsp_list = [self.get_api_response(page) for page in range(2)]
        for rsp in rsp_list:
            self.extract_hot(rsp)
        self.save_rank_data()
        self.extract_user_info()


if __name__ == '__main__':
    KwaiStartHotSpider().extract()
    KwaiStartTopSpider().extract()