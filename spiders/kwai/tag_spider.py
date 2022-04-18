#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/4/17 09:51
# @Author  : shixin.liu
# @File    : tag_spider.py
import json
from time import sleep

import requests

from spiders.kwai.extractors.user_info_extractor import TagUserInfoExtractor


class KwaiTagSpider(object):
    def __init__(self):
        self.api = "http://wxmini-api.uyouqu.com/rest/wd/wechatApp/search/feed?__NS_sig3=37276350144c39061a6a6968ac49988c2f592d12767674747b7a7963&__NS_sig3_origin=3sCt3iAAAAAAAAAAAAAAAwEQBv2b8ewCAPqvuCAAAAANgxskju/G2LkDqvp8yfyV2dgtyfr+AA1bhs5Cn7CZoA=="
        self.user_extractor = TagUserInfoExtractor()
        self.tag_list = [
            '#短剧',
            '#正能量短剧',
            '#原创短剧',
            '#快手短剧 MCN 影响力大赛',
            '#短剧 MCN 影响力大赛',
            '#快手短剧',
            '#情感短剧',
            '#短剧有好货',
            '#快手星芒短剧',
            '#快手小剧场',
            '#快手短剧寒假档',
            '#搞笑短剧'
        ]

    def download_api_info(self, query, page=0):
        headers = {
            'Host': 'wxmini-api.uyouqu.com',
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'Cookie': 'did=wxo_61aa75c357e816d9840e3da9382c61581074; preMinaVersion=v3.109.0; sid=kuaishou.wechat.app; appId=ks_wechat_small_app_2; clientid=13; client_key=f60ac815; kpn=WECHAT_SMALL_APP; kpf=OUTSIDE_ANDROID_H5; mod=MacBookPro15%2C1(); sys=macOS%2012.3.1; wechatVersion=7.0.8; language=zh_CN; brand=MacBookPro15%2C1; smallAppVersion=v3.109.0; session_key=1230d68d59830909f788d2f5f14f50e019af6b3ca0f2cd7ef1e31bb9a523288c70474ecc1b386b082066ffa6f27f4dc8a27e1a126327a29a5d864a95a93e8f8e0e98d21e5d642220e69ba08a2fef27f61574645fcb083061d0fa3486ec9f22b713e89891de77337b28053001; unionid=V2:1230088cf93e664485ec709129c0f1d60cad2eda0361d80b211652b7bf899260aff2d38a9f176eb412f5401610cdc5b11a641a128a7926d0472f442e9ded19769de4556d9da62220862fd71974931cd26830be7d8633416ded478e753ac912f4a2eedf1e5a96a74928053001; eUserStableOpenId=1230c94fd1a91fc7f91ce8ff7aadc09cf17c5fa35d1cc3ff6d51951319c0570a2b6084414041f3d0f0bb6f2deeebfb71e7c81a1250f4124831ff4b21bb1407aa4b03ce52fda52220f64f7f453e97bcae9e1781af1a52dca50bdff552c24e119da8fcd8dbea065c3628053001; openId=o5otV452-3DHBrjJ-JD3ty9a9puQ; eOpenUserId=1240f08a8593fb8daee81ad4022be6cb117f23d859f382be6e56daa65f939781c527816bbb2912682759958183b428ef2f4c95a03c872bdb3704028e8d76429ebc351a128a7926d0472f442e9ded19769de4556d9da622208373674172f9c1ff7db1ef3ada3a46bc4e2f6937ec87843f95950dd946eefd5028053001; kuaishou.wechat.app_st=ChZrdWFpc2hvdS53ZWNoYXQuYXBwLnN0EqABVM-PpRDhf9PIUDVBQQyM2uz_P99jnRp5NjbKjrU12gZL1h7JutDRSzaBVDGSku-5eIDJFS5QO-J_Egw1Ef6dm0UFjwDwJn3JBPZTcdsjCWWMvq7pn7gIR3vXCiR0bwDFEQGQExETlFOdOneBrF6kr9Cr_PaUTyxiOkQkrasffq1yU4_1_gAWCqylpe9HOEcOVXY0_Kn99HV2THQChqgu-BoSDwN9h_4XSGuG8eLTrjEiK4RAIiD6aopmo7sCkoWyzh4l1aw7MzwGJKgsI3iFcAkjTpXuPigFMAE; passToken=ChNwYXNzcG9ydC5wYXNzLXRva2VuEsAB0egEs8YjSMF-qE7EqkzuZv2JhNxRGzM79m76sklbOnLdgOeZm5lgcpVlIt4uYT-Rch6yVZr8bv932y4pbU0bY2WJUY_4lTLUfFTvqAKNS4zHPjPeZxUJTEYtrz7UywNggoJfdnVsqfbARp4T_FNJY6B1EFgPzrG8_VS1dqyzYr_96mU-wusujEC1fAq7oiXRiNWu9ejCT2XgiVzCCXhDRX55bKuJ2WCQq36zXbprC2sraLw9ov_kEgu_z5v3X5tKGhI9uCeSAkJMq5sEl6C7joj1CEIiIASMgBwsab4YbQoar0PQlkDc1LAUJg0VO-PrlFgkLh3yKAUwAQ; userId=149095745',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E217 MicroMessenger/6.8.0(0x16080000) NetType/WIFI Language/en Branch/Br_trunk MiniProgramEnv/Mac',
            'Referer': 'https://servicewechat.com/wx79a83b1a1e8a7978/583/page-frame.html',
            'Accept-Language': 'zh-cn',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        }
        payload = {
            "keyword": query,
            "pcursor": str(page) if page else "",
            "ussid": "",
            "pageSource": 3
        }
        rsp = requests.request("POST", self.api, headers=headers, data=json.dumps(payload))
        if json.loads(rsp.content).get("result") == 1:
            return rsp
        else:
            print("接口封禁,等待回复")
            print(f"接口响应内容:{rsp.content}")
            sleep(60)
            return self.download_api_info(query, page)

    def extract_user_list(self, rsp):
        data_json = json.loads(rsp.content)
        self.user_extractor.process(
            [video.get('userId') for video in data_json.get('feeds') if video.get('caption').find('#农村短剧') == -1])

    def extract(self):
        for tag in self.tag_list:
            page = 0
            while True:
                res = self.download_api_info(tag, page)
                if json.loads(res.content).get('pcursor') != 'no_more' or json.loads(res.content).get('result') != 1:
                    self.extract_user_list(res)
                else:
                    self.extract_user_list(res)
                    break
                page += 1


if __name__ == '__main__':
    KwaiTagSpider().extract()
