#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/11/24 15:08
# @Author  : v_shxliu
# @File    : crawl_sina_user.py
import random
import re
from json import loads
from time import sleep

import parsel
import pymysql

from common.downloader import Downloader

query_list = [
    # '高山滑雪',
    # '自由式滑雪',
    # '单板滑雪',
    # '跳台滑雪',
    # '越野滑雪',
    # '北欧两项',
    # '短道速滑',
    # '速度滑冰',
    # '花样滑冰',
    '冰球',
    '冰壶',
    '雪车',
    '钢架雪车',
    '雪橇',
    '冬季两项'
]


class SinaBasicSpider(Downloader):
    def __init__(self):
        super().__init__()
        self.cookie_sub_list = [
            '_2A25Mmm0KDeRhGeRI4lAU8irLwj-IHXVv7tnCrDV8PUNbmtAKLWvjkW9NUpE-ASP2Geeen7lFSNX-u0j81TGsVO6Y'
        ]

    def build_request(self):
        self.cookies = {
            'SUB': random.choice(self.cookie_sub_list)
        }
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/"
                          "92.0.4515.131 Safari/537.36",
        }

    def download(self, url, method, data=None):
        sleep(round(random.uniform(4, 5), 1))
        return super().download(url, method, data=None)

    def extract(self):
        pass


class SinaUserIdListSpider(SinaBasicSpider):
    def __init__(self):
        super().__init__()
        self.user_list = list()

    def extract(self):
        self.extract_user_id_list()

    @staticmethod
    def extract_total_page(rsp):
        pages_item = rsp.xpath('//div[@class="m-page"]/div/span/ul/li/a/text()')
        if pages_item:
            return int(re.findall('(\\d+)', pages_item[-1].get())[0])
        else:
            print("无法获取最大页数")

    def extract_user_id_list(self):
        for query in query_list:
            print("正在搜索: " + query)
            selector_list = list()
            res = self.req_search_page(query)
            selector_list.append(res)
            max_page = self.extract_total_page(res)
            if max_page:
                for page in range(2, max_page + 1):
                    next_res = self.req_search_page(query, page)
                    selector_list.append(next_res)
            for selector in selector_list:
                user_info_item = selector.xpath('//div[@id="pl_user_feedList"]//div[@class="info"]')
                for user_info in user_info_item:
                    if query in user_info.xpath('./p/text()').get():
                        self.user_list.append(
                            user_info.xpath('./div/a/@href').get().replace('//weibo.com/', '').replace('u/', ''))
                    # else:
                    #     print(query + "!=" + user_info.xpath('./p/text()').get())

    def req_search_page(self, query, page=1):
        url = 'https://s.weibo.com/user?q={}&auth=per_vip&page={}'
        res = self.download(url.format(query, page), 'GET')
        return parsel.Selector(text=res.text) if res.status_code == 200 else None


class SinaUserSpider(SinaBasicSpider):
    def __init__(self, user_list):
        super().__init__()
        self.user_list = user_list
        self.user_info = dict()
        self.conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='pass', db='spider',
                                    charset='utf8mb4')
        self.cur = self.conn.cursor()

    def extract(self):
        self.extract_user_info()

    def extract_user_info(self):
        url = 'http://weibo.com/ajax/profile/info?custom={}'
        for user_id in self.user_list:
            insert_data = dict()
            user_info = loads(self.download(url.format(user_id), 'get').text)['data']
            try:
                insert_data['id'] = user_info['user']['idstr']
            except KeyError:
                continue
            insert_data['fans_count'] = user_info['user']['followers_count']
            insert_data['statuses_count'] = user_info['user']['statuses_count']
            insert_data['identity'] = user_info['user']['verified_reason']
            insert_data['nickname'] = user_info['user']['screen_name']
            insert_data['intro'] = user_info['user']['description']
            insert_data['url'] = "https://weibo.com" + user_info['user']['profile_url']
            insert_data['crawl_source'] = "search"
            try:
                insert_data['top_note'] = self.extract_statuses(insert_data['id'])
            except KeyError:
                insert_data['top_note'] = ''

            try:
                sql = '''INSERT IGNORE INTO sina_user {} '''.format(tuple(insert_data.keys())).replace("'", '')
                sql += '''VALUES {} '''.format(tuple(insert_data.values()))
                sql += '''ON DUPLICATE KEY UPDATE `intro`='{}',`nickname`='{}',modify_time=now(),`top_note`='{}',`url`='{}' '''.format(
                    insert_data['intro'], insert_data['nickname'], insert_data['top_note'], insert_data['url'])
                self.cur.execute(sql)
                print("{} 资料入库成功".format(insert_data['nickname']))
                self.conn.commit()
            except pymysql.err.OperationalError:
                print(insert_data)
                print(sql)
            except pymysql.err.ProgrammingError:
                print(insert_data)
                print(sql)

    def extract_statuses(self, user_id):
        url = 'https://weibo.com/ajax/statuses/mymblog?uid={}'
        statuses = loads(self.download(url.format(user_id), 'get').content)['data']['list']
        top_status = [status['text_raw'] for status in statuses if status['user']['idstr'] == user_id]
        return ';'.join(top_status[:2]) if len(top_status) > 3 else ';'.join(top_status)


if __name__ == '__main__':
    user_search_spider = SinaUserIdListSpider()
    user_search_spider.extract()
    user_spider = SinaUserSpider(user_search_spider.user_list)
    user_spider.extract()
