#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/8/20 10:50
# @Author  : v_shxliu
# @File    : xiaohongshu.py
import json
import re
from urllib.parse import quote

import pymysql
import requests

from time import sleep, time

from retry import retry

from common import sign
from common.downloader import Downloader
from spiders.redbook_user_info import RedBookUser
import random

query_list = [
    '冬奥',
    '冬奥会',
    '北京冬奥会',
    '2022北京冬奥会',
    '冬季奥运会',
    '索契',
    '平昌',
    '盐湖城',
    '都灵',
    '温哥华',
    '冬奥吉祥物',
    '冰墩墩',
    '雪容融',
    '开幕式',
    '闭幕式',
    '北京',
    '张家口',
    '雪车',
    '冰壶',
    '冰球',
    '雪橇',
    '滑冰',
    '滑雪',
    '花滑',
    '速度滑冰',
    '短道速滑',
    '花样滑冰',
    '自由式滑雪',
    '高山滑雪',
    '越野滑雪',
    '单板滑雪',
    '跳台滑雪',
    '冬季两项',
    '北欧两项',
    '钢架雪车',
    '裁判',
    '运动员',
    '选手',
    '奥组委',
    '教练',
    '主帅',
    '冠军',
    '夺冠',
    '解说',
    '韩国',
    '加拿大',
    '美国',
    '日本',
    '高亭宇',
    '张虹',
    '羽生结弦',
    '宁忠岩',
    '杨扬',
    '李子君',
    '徐梦桃',
    '武绍桐',
    '耿文强',
    '麻敬宜',
    '曲春雨',
    '陈虹伊',
    '王心迪',
    '刘佳宇',
    '王芮',
    '范可新',
    '朱易',
    '张可欣',
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
    '云顶',
    '首钢',
    '奥运村',
    '冰立方',
    '体育',
    '奥运冠军'
]
tag_list = [
    'homefeed.travel_v2',
    'homefeed.mens_fashion_v2',
    'homefeed.fitness_v2',
    'homefeed.movies_v2',
    'homefeed.car_v2',
    'homefeed.digital_v2',
    'homefeed.home_v2',
    'homefeed.books_v2',
    'homefeed.food_v2',
    'homefeed.skincare_v2',
    'homefeed.music_v2',
    'homefeed.celebrities_v2',
    'homefeed.fashion_v2',
    'homefeed.pets_v2',
    'homefeed.baby_v2',
    'homefeed.maternity_v2',
    'homefeed.weddings_v2',
    'homefeed.cosmetics_v2',
    'recommend_v2',
]
ua_list = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Mobile/12A365 MicroMessenger/5.4.1 NetType/WIF",
    "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Mobile Safari/537.36 MicroMessenger/6.0.0.54_r849063.501 NetType/WIFI"
]
auth_list = ['wxmp.8a2c5425-c9a1-449b-ba81-26e4f15c6836']
headers = {
    "content-type": "application/json",
    "referer": "https://servicewechat.com/wxb296433268a1c654/58/page-frame.html",
}


def generate_timestamp():
    print('生成列表页时间戳...')
    sleep(round(random.uniform(1, 2), 1))
    time_stamp = time()
    return round(time_stamp, 3)
    # return "1631693085.391"


def extract_user_list():
    base_api = '/fe_api/burdock/weixin/v2/homefeed/personalNotes?category={}&cursorScore={}&geo=&page={}&pageSize=20&needGifCover=true'
    tag = random.choice(tag_list)
    apis = [
        base_api.format(tag, '', page_num) if page_num == 1 else base_api.format(tag, generate_timestamp(), page_num)
        for page_num in range(1, 3)]
    user_id_list = list()
    page = 0
    for api in apis:
        page += 1
        x_sign = sign.generate_x_sign(api)
        headers['x-sign'] = x_sign
        headers['user-agent'] = random.choice(ua_list)
        headers['authorization'] = random.choice(auth_list)
        print("解析列表第{}页".format(page))
        sleep(round(random.uniform(1, 10), 1))
        res = requests.get('http://www.xiaohongshu.com' + api, headers=headers, timeout=(10, 20))
        print("请求api:{}".format('http://www.xiaohongshu.com' + api))
        print("sign:{}".format(x_sign))
        res_obj = json.loads(res.content)
        if res_obj.get('success'):
            user_id_list += set([video.get('user').get('id') for video in res_obj.get('data', [])])
        else:
            continue
    if user_id_list:
        return set(user_id_list)
    else:
        raise Exception('拉取列表页失败')


def get_proxy():
    with open('../common/proxy1', 'r') as fp:
        proxy = fp.readline()
    return {
        'http': proxy,
        'https': proxy,
    }


@retry(tries=3)
def change_proxy():
    proxy_api = 'http://route.xiongmaodaili.com/xiongmao-web/api/glip?secret=b98b87874128d8387000ea2713835e19&orderNo' \
                '=GL20201113201434Ln043IBh&count=1&isTxt=0&proxyType=1'
    proxy_rsp = requests.get(proxy_api, tiemout=(10, 10))
    rsp_json = json.loads(proxy_rsp.content)
    if rsp_json.get('code') == '0':
        proxy = 'http://' + rsp_json['obj'][0]['ip'] + ':' + str(rsp_json['obj'][0]['port'])
        with open('../common/proxy1', 'w') as fp:
            fp.write(proxy)


def request_query(url):
    rsp = requests.Response()
    downloader = Downloader()
    x_sign = sign.generate_x_sign(url)
    print("请求api:{}".format('http://www.xiaohongshu.com' + url))
    print("sign:{}".format(x_sign))
    downloader.headers['x-sign'] = x_sign
    downloader.headers['user-agent'] = random.choice(ua_list)
    downloader.headers['authorization'] = random.choice(auth_list)
    proxy = get_proxy()
    # proxy = {}
    try:
        rsp = downloader.download('http://www.xiaohongshu.com' + url, 'get', '', proxy)
        while 500 >= rsp.status_code >= 400 and rsp.status_code != 403:
            # input('请求失败 请前往小红书小程序校验')
            print("代理失效,更换代理....")
            change_proxy()
            proxy = get_proxy()
            print("代理更换为{}".format(proxy))
            try:
                rsp = downloader.download('http://www.xiaohongshu.com' + url, 'get', '', proxy)
            except requests.exceptions.ReadTimeout:
                print("代理失效,更换代理....")
                change_proxy()
                proxy = get_proxy()
                print("代理更换为{}".format(proxy))
    except requests.exceptions.ReadTimeout:
        print("代理失效,更换代理....")
        change_proxy()
        proxy = get_proxy()
        print("代理更换为{}".format(proxy))
    # sleep(round(random.uniform(2, 4), 1))
    return rsp


def extract_total_page(res):
    res_obj = json.loads(res.content)
    total_count = res_obj.get('data', {}).get('totalCount')
    return total_count // 20 if total_count % 20 == 0 else total_count // 20 + 1


def extract_user_id(res, search_type):
    if res.status_code == 200:
        res_obj = json.loads(res.content)
        if search_type == 'user':
            return set([user_item.get('id') for user_item in res_obj.get('data', {}).get('users', []) if
                        user_item.get('desc', '') != ''])
        else:
            return set(
                [note_item.get('user', {"id": ""}).get('id') for note_item in res_obj.get('data', {}).get('notes', [])])
    else:
        print("请求异常")
        print(res.content)
        return []


def get_note_list(user_id):
    note_item_list = list()
    page = 0

    while True:
        page += 1
        base_api = '/fe_api/burdock/weixin/v2/user/{}/notes?page={}'.format(user_id, page)
        notes_rsp = request_query(base_api)
        if notes_rsp.status_code == 200:
            note_data = json.loads(notes_rsp.content).get('data', None)
            note_code = json.loads(notes_rsp.content).get('code', None)
        else:
            break
        if note_data:
            note_item_list += note_data
        elif note_code != -1:
            break
        else:
            print('跳过此次循环')
            print(note_code)
            print(note_data)
            continue
    return note_item_list


def get_comment(note_id):
    comment_list = list()
    # while True:
    base_api = '/fe_api/burdock/weixin/v2/notes/{}/comments?pageSize=10'.format(note_id)
    comment_rsp = request_query(base_api)
    if comment_rsp.status_code == 200:
        comment_data = json.loads(comment_rsp.content).get('data', None)
        if comment_data and comment_data.get('comments'):
            for comment in comment_data.get('comments'):
                comment_list.append(comment['user'])
                for sub_comment in comment['subComments']:
                    comment_list.append(sub_comment['user'])
    # else:
    #     break
    # sleep(round(random.uniform(4, 5), 1))
    return comment_list


def get_note_comment(user_id):
    user_list = list()
    note_list = get_note_list(user_id)
    for note in note_list:
        user_list += get_comment(note['id'])
    user_list = [user['id'] for user in user_list if user['id'] != user_id]
    return set(user_list)


def search_query(url, search_type):
    user_id_list = list()
    res = request_query(url)
    ids = extract_user_id(res, search_type)
    if ids:
        user_id_list += ids
        total_page = 10 if extract_total_page(res) > 10 else extract_total_page(res)
        if total_page > 1:
            urls = [re.sub('page=\\d+', 'page=' + str(page), url) for page in range(1, total_page)]
            for url in urls:
                sleep(round(random.uniform(4, 5), 1))
                res = request_query(url)
                user_id_list += extract_user_id(res, search_type)
    if user_id_list:
        return set(user_id_list)
    else:
        print('拉取列表页失败')
        return []


def search_user_list(query):
    base_url = "/fe_api/burdock/weixin/v2/search/users?keyword={}&page=1&pageSize=20"
    url = base_url.format(quote(query))
    return search_query(url, 'user')


def search_note_list(query):
    base_url = "/fe_api/burdock/weixin/v2/search/notes?keyword={}&sortBy=general&page=1" \
               "&pageSize=20&prependNoteIds=&needGifCover=true"
    url = base_url.format(quote(query))
    return search_query(url, 'note')


# def main():
#     user = RedBookUser('KOL')
#     user_id_list = extract_user_list()
#     for user_id in user_id_list:
#         sleep(round(random.uniform(2, 5), 1))
#         user.parse(user_id)

def main():
    user = RedBookUser('KOL')
    user.cur.execute('''select distinct url,id from red_book_user where is_dispatched = '0' 
    order by create_time desc limit 40001,80000 ''')
    user_urls = user.cur.fetchall()
    for user_url in user_urls:
        uid = user_url[0].replace('https://www.xiaohongshu.com/user/profile/', '')
        user_id_list = get_note_comment(uid)
        for comment_user_id in user_id_list:
            # sleep(round(random.uniform(1, 2), 1))
            user.parse(comment_user_id)
        sql = '''update `red_book_user` set `is_dispatched` = '1' where `id` = '{}' '''.format(user_url[1])
        user.cur.execute(sql)
        user.conn.commit()


if __name__ == '__main__':
    main()
    # print(get_proxy())
    # change_proxy()
    # print(get_proxy())
    # while True:
    #     try:
    #         main()
    #         # sleep(600)
    #     except Exception as e:
    #         print(e)
    #         continue
    # main()
