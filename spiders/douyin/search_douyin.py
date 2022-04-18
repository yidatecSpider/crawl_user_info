#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/11/1 10:36
# @Author  : v_shxliu
# @File    : search_douyin.py
import json

import pymysql

from spiders.douyin.run import Sign

query_list = [
    # '冬奥',
    # '冬奥会',
    # '北京冬奥会',
    # '2022北京冬奥会',
    # '冬季奥运会',
    # '索契冬奥会',
    # '平昌冬奥会',
    # '盐湖城冬奥会',
    # '都灵冬奥会',
    # '温哥华冬奥会',
    # '冬奥吉祥物',
    # '冰墩墩',
    # '雪容融',
    # '冬奥会开幕式',
    # '冬奥会闭幕式',
    # '张家口冬奥会',
    # '雪车',
    # '冰壶',
    # '冰球',
    # '雪橇',
    # '滑冰',
    # '滑雪',
    # '花滑',
    # '速度滑冰',
    # '短道速滑',
    # '花样滑冰',
    # '自由式滑雪',
    # '高山滑雪',
    # '越野滑雪',
    # '单板滑雪',
    # '跳台滑雪',
    # '冬季两项',
    # '北欧两项',
    # '钢架雪车',
    # '冬奥会裁判',
    # '冬奥会运动员',
    # '冬奥会选手',
    # '冬奥会奥组委',
    # '冬奥会教练',
    # '冬奥会主帅',
    # '奥运冠军',
    # '奥运夺冠',
    # '冬奥会解说',
    # '韩国冬奥会',
    # '加拿大冬奥会',
    # '美国冬奥会',
    # '日本冬奥会',
    # '高亭宇',
    # '张虹',
    # '羽生结弦',
    # '宁忠岩',
    # '杨扬',
    # '李子君',
    # '徐梦桃',
    # '武绍桐',
    # '耿文强',
    # '麻敬宜',
    # '曲春雨',
    # '陈虹伊',
    # '王心迪',
    # '刘佳宇',
    # '王芮',
    # '范可新',
    # '朱易',
    # '张可欣',
    '蔡雪桐',
    '王诗玥',
    '柳鑫宇',
    '王濛',
    '齐广璞',
    '贾宗洋',
    '孔凡钰',
    '雪场',
    '滑雪场',
    '冰场',
    '滑冰场',
    '鸟巢',
    '国家速滑馆',
    '冰丝带',
    '雪如意',
    '奥运村',
    '冰立方',
    '体育',
    '奥运冠军'
]


class CrawlDouYin(object):
    def __init__(self):
        self._method = None
        self.sign = Sign()

    def extract(self, kw):
        pass

    def set_method(self, method):
        self._method = method


class CrawlDouYinSearch(CrawlDouYin):
    def __init__(self):
        super().__init__()
        self._user_list = list()

    @property
    def user_list(self):
        return self._user_list


class CrawlDouYinSearchItem(CrawlDouYinSearch):
    """
    通过关键字检索相关视频,提取坐着sec_id
    """

    def __init__(self):
        super().__init__()
        self._method = 'search_item'

    def extract(self, kw):
        content = self.sign.dy_sign(method=self._method, kw=kw)
        search_user = CrawlDouYinSearchUser()
        json_data = json.loads(content)
        if json_data['status_code'] == 0:
            video_list = json_data.get('data', [])
            for video_item in video_list:
                nickname = video_item['aweme_info']['author']['nickname']
                search_user.extract(nickname)
                self._user_list.append(search_user.user_list[0])


class CrawlDouYinSearchUser(CrawlDouYinSearch):
    def __init__(self):
        super().__init__()
        self._method = 'search_user'

    def extract(self, kw):
        try:
            content = self.sign.dy_sign(method=self._method, kw=kw)
            json_data = json.loads(content)
        except Exception as e:
            print("错误内容:" + content)
            print(e)
            raise
        if json_data['status_code'] == 0:
            user_list = json_data.get('user_list', [])
            self._user_list = [
                {
                    "sec_uid": user_item['user_info']['sec_uid'],
                    "user_info": {
                        "nick_name": user_item['user_info']['nickname'],
                        "signature": user_item['user_info']['signature'],
                        "follower_count": user_item['user_info']['follower_count'],
                    }
                } for user_item in user_list]


class CrawlDouYinUserInfo(CrawlDouYin):
    def __init__(self):
        super().__init__()
        self._insert_data = dict()
        self._method = 'aweme_post'
        self.conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='pass', db='spider',
                                    charset='utf8mb4')
        self.cur = self.conn.cursor()

    def __del__(self):
        self.cur.close()
        self.conn.close()

    def extract(self, user_item):
        content = self.sign.dy_sign(method=self._method, kw=user_item['sec_uid'])
        json_data = json.loads(content)
        if json_data['status_code'] == 0 and json_data['aweme_list']:
            video_list = json_data['aweme_list'][:3] if len(json_data['aweme_list']) > 3 else json_data['aweme_list']
            top_video = ';'.join([video['desc'] for video in video_list])
            self._insert_data['id'] = user_item['sec_uid']
            self._insert_data['fans_count'] = user_item['user_info']['follower_count']
            self._insert_data['nickname'] = user_item['user_info']['nick_name']
            self._insert_data['top_title'] = top_video
            self._insert_data['intro'] = user_item['user_info']['signature']
            try:
                sql = '''INSERT IGNORE INTO douyin_user {} '''.format(tuple(self._insert_data.keys())).replace("'", '')
                sql += '''VALUES {} '''.format(tuple(self._insert_data.values()))
                sql += '''ON DUPLICATE KEY UPDATE `intro`='{}',`nickname`='{}',modify_time=now(),`top_title`='{}' '''.format(
                    self._insert_data['intro'], self._insert_data['nickname'], self._insert_data['top_title'])
                self.cur.execute(sql)
                print("{} 资料入库成功".format(self._insert_data['nickname']))
                self.conn.commit()
            except pymysql.err.OperationalError:
                print(self._insert_data)
                print(sql)
            except pymysql.err.ProgrammingError:
                print(self._insert_data)
                print(sql)


if __name__ == '__main__':
    search_item_spider = CrawlDouYinSearchItem()
    search_user_spider = CrawlDouYinSearchUser()
    user_spider = CrawlDouYinUserInfo()
    for query in query_list:
        print("抓取关键词:" + query)
        try:
            search_item_spider.extract(query)
            search_user_spider.extract(query)
            user_set = search_user_spider.user_list + search_item_spider.user_list
            for user in user_set:
                user_spider.extract(user)
        except Exception as e:
            print(e)
            print("失败query:" + query)
            continue
