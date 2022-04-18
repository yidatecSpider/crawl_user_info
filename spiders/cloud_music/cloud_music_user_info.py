#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/8/26 15:23
# @Author  : v_shxliu
# @File    : cloud_music_user_info.py
import json
from time import sleep

from common.downloader import Downloader
from common.params import Params


class UserInfo(object):
    def __init__(self, user_id):
        self.downloader = Downloader()
        self.params = Params()
        self.api_data = dict()
        self.user_id = user_id
        self.head_info_api = "https://music.163.com/weapi/artist/head/info/get"
        self.follow_count_api = "https://music.163.com/weapi/artist/follow/count/get"
        self.identity_api = "https://music.163.com/weapi/block/personal/base/info/identity/get"
        self.detail_info_api = "https://music.163.com/weapi/block/personal/artist/baike/info/detail/get"

    @staticmethod
    def transform_field(field_name):
        transform_dict = {
            u"艺人名": "user_name",
            u"昵称": "nickname",
            u"性别": "sex",
            u"村龄": "id_age",
            u"生日": "birthday",
            u"地区": "location",
            u"社交账号": "out_site_url",
            u"个人简介": "intro",
            u"学校": "school",
        }
        return transform_dict.get(field_name.replace(':', ''), None)

    def request_api(self, url, params):
        self.params.generate_params(params)
        data = {
            "params": self.params.params,
            "encSecKey": self.params.sec_key
        }
        return self.downloader.download(url, "POST", data)

    def parse_head_info(self):
        res = self.request_api(self.head_info_api, {"id": self.user_id})
        self.api_data['head_info'] = json.loads(res.content)

    def parse_follow_count(self):
        res = self.request_api(self.follow_count_api, {"id": self.user_id})
        self.api_data['follow_count'] = json.loads(res.content)

    def parse_identity(self):
        res = self.request_api(self.identity_api, {"id": self.user_id, "type": 1})
        self.api_data['identity'] = json.loads(res.content)

    def parse_detail_info(self):
        res = self.request_api(self.detail_info_api, {"artistId": self.user_id})
        self.api_data['detail_info'] = json.loads(res.content)

    def parse(self):
        self.parse_head_info()
        self.parse_follow_count()
        self.parse_identity()
        self.parse_detail_info()
        user_info = dict()
        user_data = self.api_data['head_info']['data'].get('user')
        user_info['nickname'] = user_data.get('nickname') if user_data else ''
        user_info['id'] = self.user_id
        user_info['url'] = "https://music.163.com/user/home?id=" + self.user_id
        user_info['album_count'] = self.api_data['head_info']['data']['artist']['albumSize']
        user_info['music_count'] = self.api_data['head_info']['data']['artist']['musicSize']
        user_info['mv_count'] = self.api_data['head_info']['data']['artist']['mvSize']
        user_info['fans_count'] = self.api_data['follow_count']['data']['fansCnt']
        try:
            user_info['identity'] = ';'.join([identity_item['uiElement']['mainTitle']['title'] for identity_item in
                                              self.api_data['identity']['data']['resources']])
        except TypeError:
            user_info['identity'] = ""
        for detail_item in self.api_data['detail_info']['data']['resources']:
            field = self.transform_field(detail_item['uiElement']['mainTitle']['title'])
            if field:
                if detail_item['uiElement']['subTitles'] is not None:
                    user_info[field] = ';'.join(
                        [sub_title_item.get('title') for sub_title_item in detail_item['uiElement']['subTitles']])
                else:
                    user_info[field] = ''
        return user_info


if __name__ == '__main__':
    import pymysql

    conn = pymysql.connect(host='127.0.0.1', port=3306, user='develop', passwd='pass', db='spider')
    cur = conn.cursor()
    with open('../search_user_id.txt', 'r+', encoding='utf-8') as fp:
        for user_id in fp:
            user_id = user_id.replace('\n', '')
            print("id: %s,开始抓取" % user_id)
            try:
                save_data = UserInfo(user_id).parse()
            except KeyError:
                with open("../fail_case.txt", "a") as ffp:
                    ffp.writelines(user_id + "\n")
                continue
            # sleep(1)
            # print("{} 资料抓取成功".format(save_data['user_name']))
            sql = '''INSERT IGNORE INTO cloud_music_user {} '''.format(tuple(save_data.keys())).replace("'", '')
            sql += '''VALUES {}'''.format(tuple(save_data.values()))
            cur.execute(sql)
            print("{} 资料入库成功".format(save_data['user_name']))
            conn.commit()
    cur.close()
    conn.close()
