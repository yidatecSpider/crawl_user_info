#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/14 16:45
# @Author  : v_shxliu
# @File    : redbook_user_info.py
import json

import pymysql
import requests

from common import sign
from common.downloader import Downloader


class RedBookUser(object):
    headers = {
        "authorization": "wxmp.8a2c5425-c9a1-449b-ba81-26e4f15c6836",
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 "
                      "Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat",
        "content-type": "application/json",
        # "referer": "https://servicewechat.com/",
    }

    def __init__(self, source):
        self.downloader = Downloader()
        self.conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='pass', db='spider',
                                    charset='utf8mb4')
        self.cur = self.conn.cursor()
        self.insert_data = dict()
        self.user_info_api = "/fe_api/burdock/weixin/v2/user/{}"
        self.source = source

    def __del__(self):
        self.cur.close()
        self.conn.close()

    def parse_user_note(self, user_id):
        note_api = "/fe_api/burdock/weixin/v2/user/{}/notes?page=1&page_size=3".format(user_id)
        x_sign = sign.generate_x_sign(note_api)
        self.headers['x-sign'] = x_sign
        res = requests.get('http://www.xiaohongshu.com' + note_api, headers=self.headers)
        notes_json = json.loads(res.content)
        note_list = notes_json['data'][0:3] if len(notes_json.get('data', [])) > 3 else notes_json.get('data', [])
        self.insert_data['top_note'] = ';'.join([note_item.get('title', '') for note_item in note_list])

    def parse(self, user_id):
        from spiders.red_book import request_query
        res = request_query(self.user_info_api.format(user_id))
        if res.status_code == 200:
            self.transform(res)
            self.parse_user_note(user_id)
            sql = None
            try:
                sql = '''INSERT IGNORE INTO red_book_user {} '''.format(tuple(self.insert_data.keys())).replace("'", '')
                sql += '''VALUES {} '''.format(tuple(self.insert_data.values()))
                sql += '''ON DUPLICATE KEY UPDATE `intro`='{}',`nickname`='{}',modify_time=now(),`top_note`='{}', 
                `fans_count`='{}',`like_count`='{}' '''.format(
                    self.insert_data['intro'], self.insert_data['nickname'], self.insert_data['top_note'],
                    self.insert_data['fans_count'], self.insert_data['like_count'])
                self.cur.execute(sql)
                print("{} 资料入库成功".format(self.insert_data['nickname']))
                self.conn.commit()
            except pymysql.err.OperationalError:
                print(self.insert_data)
                print(sql)
            except pymysql.err.ProgrammingError:
                print(self.insert_data)
                print(sql)

    def transform(self, res):
        json_data = json.loads(res.content).get('data')
        if json_data:
            self.insert_data['id'] = json_data.get('red_id')
            self.insert_data['note_count'] = json_data.get('notes')
            self.insert_data['fans_count'] = json_data.get('fans')
            self.insert_data['like_count'] = json_data.get('liked')
            self.insert_data['identity'] = json_data.get('level').get('name') if json_data.get(
                'level') else ''
            self.insert_data['nickname'] = json_data.get('nickname')
            self.insert_data['intro'] = json_data.get('desc')
            self.insert_data['url'] = "https://www.xiaohongshu.com/user/profile/" + json_data.get('id')
            if not self.insert_data['identity']:
                self.insert_data['identity'] = ''
            self.insert_data['crawl_source'] = self.source


if __name__ == '__main__':
    user = RedBookUser('test')
    user.parse('5fb3f3250000000001002c34')