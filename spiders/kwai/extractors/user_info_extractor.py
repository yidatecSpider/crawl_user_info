#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/4/17 09:51
# @Author  : shixin.liu
# @File    : user_info_extractor.py
import json
from json import loads
from time import sleep

import pymysql
import requests

from common.hashlib_get_id import get_raw_video_id


class BaseUserInfoExtractor(object):
    name = ''

    def __init__(self):
        self.api = "http://wxmini-api.uyouqu.com/rest/wd/wechatApp/user/profile?__NS_sig3=40501427a6682271911d1e1fa1b3bd785c7f3665010103030c0d0e14&__NS_sig3_origin=3sCt3iAAAAAAAAAAAAAAAwEQBv2b8ewClMXKayAAAAAJi0stjOHG3rgHqKgqzfXD2NV/y6qpBg0O3MgXxLad8A=="
        self.user_info_list = []
        self.conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='pass', db='spider',
                                    charset='utf8mb4')
        self.cur = self.conn.cursor()

    def download_user_info(self, user_id):
        sleep(2)
        headers = {
            'Host': 'wxmini-api.uyouqu.com',
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'Cookie': 'did=wxo_61aa75c357e816d9840e3da9382c61581074; preMinaVersion=v3.105.0; sid=kuaishou.wechat.app; appId=ks_wechat_small_app_2; clientid=13; client_key=f60ac815; kpn=WECHAT_SMALL_APP; kpf=OUTSIDE_ANDROID_H5; mod=MacBookPro15%2C1(); sys=macOS%2012.2.1; wechatVersion=7.0.8; language=zh_CN; brand=MacBookPro15%2C1; smallAppVersion=v3.105.0; session_key=1230d68d59830909f788d2f5f14f50e019af6b3ca0f2cd7ef1e31bb9a523288c70474ecc1b386b082066ffa6f27f4dc8a27e1a126327a29a5d864a95a93e8f8e0e98d21e5d642220e69ba08a2fef27f61574645fcb083061d0fa3486ec9f22b713e89891de77337b28053001; unionid=V2:1230088cf93e664485ec709129c0f1d60cad2eda0361d80b211652b7bf899260aff2d38a9f176eb412f5401610cdc5b11a641a128a7926d0472f442e9ded19769de4556d9da62220862fd71974931cd26830be7d8633416ded478e753ac912f4a2eedf1e5a96a74928053001; eUserStableOpenId=1230c94fd1a91fc7f91ce8ff7aadc09cf17c5fa35d1cc3ff6d51951319c0570a2b6084414041f3d0f0bb6f2deeebfb71e7c81a1250f4124831ff4b21bb1407aa4b03ce52fda52220f64f7f453e97bcae9e1781af1a52dca50bdff552c24e119da8fcd8dbea065c3628053001; openId=o5otV452-3DHBrjJ-JD3ty9a9puQ; eOpenUserId=1240f08a8593fb8daee81ad4022be6cb117f23d859f382be6e56daa65f939781c527816bbb2912682759958183b428ef2f4c95a03c872bdb3704028e8d76429ebc351a128a7926d0472f442e9ded19769de4556d9da622208373674172f9c1ff7db1ef3ada3a46bc4e2f6937ec87843f95950dd946eefd5028053001; kuaishou.wechat.app_st=ChZrdWFpc2hvdS53ZWNoYXQuYXBwLnN0EqABVM-PpRDhf9PIUDVBQQyM2uz_P99jnRp5NjbKjrU12gZL1h7JutDRSzaBVDGSku-5eIDJFS5QO-J_Egw1Ef6dm0UFjwDwJn3JBPZTcdsjCWWMvq7pn7gIR3vXCiR0bwDFEQGQExETlFOdOneBrF6kr9Cr_PaUTyxiOkQkrasffq1yU4_1_gAWCqylpe9HOEcOVXY0_Kn99HV2THQChqgu-BoSDwN9h_4XSGuG8eLTrjEiK4RAIiD6aopmo7sCkoWyzh4l1aw7MzwGJKgsI3iFcAkjTpXuPigFMAE; passToken=ChNwYXNzcG9ydC5wYXNzLXRva2VuEsAB0egEs8YjSMF-qE7EqkzuZv2JhNxRGzM79m76sklbOnLdgOeZm5lgcpVlIt4uYT-Rch6yVZr8bv932y4pbU0bY2WJUY_4lTLUfFTvqAKNS4zHPjPeZxUJTEYtrz7UywNggoJfdnVsqfbARp4T_FNJY6B1EFgPzrG8_VS1dqyzYr_96mU-wusujEC1fAq7oiXRiNWu9ejCT2XgiVzCCXhDRX55bKuJ2WCQq36zXbprC2sraLw9ov_kEgu_z5v3X5tKGhI9uCeSAkJMq5sEl6C7joj1CEIiIASMgBwsab4YbQoar0PQlkDc1LAUJg0VO-PrlFgkLh3yKAUwAQ; userId=149095745',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E217 MicroMessenger/6.8.0(0x16080000) NetType/WIFI Language/en Branch/Br_trunk MiniProgramEnv/Mac',
            'Referer': 'https://servicewechat.com/wx79a83b1a1e8a7978/579/page-frame.html',
            'Accept-Language': 'zh-cn',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        }
        payload = json.dumps({
            "eid": user_id
        })
        print(f"请求用户ID:{user_id}")
        rsp = requests.post(self.api, headers=headers, data=payload)
        if loads(rsp.content).get("result") == 1:
            return rsp
        else:
            print("接口封禁,等待回复")
            print(f"接口响应内容:{rsp.content}")
            sleep(60)
            return self.download_user_info(user_id)

    def extract_user_info(self, rsp):
        user_info = {}
        user_json = loads(rsp.content)
        user_profile = user_json.get('userProfile', {})
        user_info['id'] = user_profile.get('profile', {}).get('user_id', '')
        user_info['kwai_id'] = user_profile.get('profile', {}).get('kwaiId')
        user_info['hash_code'] = get_raw_video_id(user_info['id'])
        user_info['note_count'] = user_profile.get('ownerCount', {}).get('photo')
        user_info['fans_count'] = user_profile.get('ownerCount', {}).get('fan')
        user_info['like_count'] = user_profile.get('ownerCount', {}).get('like')
        user_info['area'] = user_profile.get('cityName')
        user_info['constellation'] = user_profile.get('constellation')
        user_info['identity'] = user_profile.get('profile', {}).get('verifiedDetail', {}).get('description')
        user_info['nickname'] = user_profile.get('profile', {}).get('user_name')
        user_info['sex'] = user_profile.get('profile', {}).get('user_sex')
        user_info['intro'] = user_profile.get('profile', {}).get('user_text')
        user_info['crawl_source'] = self.name
        self.user_info_list.append(user_info)

    def save_user_info(self):
        sql = None
        try:
            sql = '''insert into kwai_user_info(`id`,`kwai_id`,`hash_code`,`note_count`,`fans_count`,`like_count`,`area`
            ,`constellation`,`identity`,`nickname`,`sex`,`intro`,`crawl_source`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) 
            ON DUPLICATE KEY UPDATE `kwai_id` = VALUES(`kwai_id`),`note_count` = VALUES(`note_count`),
            `fans_count` = VALUES(`fans_count`),`like_count` = VALUES(`like_count`),`area` = VALUES(`area`)
             ,`identity` = VALUES(`identity`),`nickname` = VALUES(`nickname`),`intro` = VALUES(`intro`)'''
            self.cur.executemany(sql, [tuple(insert_data.values()) for insert_data in self.user_info_list])
            print(f"{','.join([insert_data['nickname'] for insert_data in self.user_info_list])}入库成功")
            self.conn.commit()
        except pymysql.err.OperationalError:
            print(sql)
        except pymysql.err.ProgrammingError:
            print(sql)
        except pymysql.err.InterfaceError:
            self.conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='pass', db='spider',
                                        charset='utf8mb4')
            self.cur = self.conn.cursor()
        finally:
            self.user_info_list = []

    def process(self, user_id_list) -> None:
        """
        入口函数
        :param user_id_list:用户id列表
        """
        user_rsp_list = [self.download_user_info(user_id) for user_id in user_id_list]
        for rsp in user_rsp_list:
            self.extract_user_info(rsp)
        self.save_user_info()


class TopListUserInfoExtractor(BaseUserInfoExtractor):
    name = 'Top50'
    pass


class HotListUserInfoExtractor(BaseUserInfoExtractor):
    name = 'Hot'
    pass


class TagUserInfoExtractor(BaseUserInfoExtractor):
    name = 'tag'


class IdentityUserInfoExtractor(BaseUserInfoExtractor):
    name = 'identity'


class IntroUserInfoExtractor(BaseUserInfoExtractor):
    name = 'intro'


if __name__ == '__main__':
    extractor = TopListUserInfoExtractor()
    extractor.process(["1339385328"])
