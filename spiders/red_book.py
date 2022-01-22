#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/8/20 10:50
# @Author  : v_shxliu
# @File    : xiaohongshu.py
import json
import re
from urllib.parse import quote
import requests
from time import sleep, time,strftime,localtime
from retry import retry
from common import sign
from common.downloader import Downloader
from common.utils import get_proxy
from spiders.redbook_user_info import RedBookUser
import random
import threading

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
auth_list = [
    'wxmp.8a2c5425-c9a1-449b-ba81-26e4f15c6836',
    # 'wxmp.907545e0-6716-40e2-91e5-cd59b7345bd1'
]
headers = {
    "content-type": "application/json",
    # "referer": "https://servicewechat.com/wxb296433268a1c654/58/page-frame.html",
}


def generate_timestamp():
    print('生成列表页时间戳...')
    sleep(round(random.uniform(1, 2), 1))
    time_stamp = time()
    return round(time_stamp, 3)


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
        res = requests.get('http://www.xiaohongshu.com' + api, headers=headers)
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


def request_query(url, tries=3):
    downloader = Downloader()
    proxy, auth = get_proxy()
    x_sign = sign.generate_x_sign(url)
    print(f'[{strftime("%Y-%m-%d %H:%M:%S", localtime())}]请求api:{"http://www.xiaohongshu.com" + url}')
    print("sign:{}".format(x_sign))
    downloader.headers['Proxy-Authorization'] = auth
    downloader.headers['x-sign'] = x_sign
    downloader.headers['user-agent'] = random.choice(ua_list)
    downloader.headers['authorization'] = random.choice(auth_list)
    proxy = {
        "http": proxy,
        "https": proxy
    }
    proxy = {}
    try:
        rsp = downloader.download('http://www.xiaohongshu.com' + url, 'get', '', proxy)
        while rsp.status_code != 200 and rsp.status_code != 403 and rsp.status_code != 423 and tries >= 1:
            # print(f"程序执行:{time() - start_time}s 被封")
            rsp = request_query(url, tries - 1)
    except requests.exceptions.ProxyError:
        rsp = request_query(url)
    except requests.exceptions.Timeout:
        rsp = request_query(url)
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


def get_comment(comment_data):
    comment_list = list()
    if comment_data and comment_data.get('comments'):
        for comment in comment_data.get('comments'):
            comment_list.append(comment['user'])
            for sub_comment in comment['subComments']:
                comment_list.append(sub_comment['user'])
    return comment_list


def request_comment_api(note_id, end_id=None):
    if end_id:
        base_api = '/fe_api/burdock/weixin/v2/notes/{}/comments?pageSize=10&endId={}'.format(note_id, end_id)
    else:
        base_api = '/fe_api/burdock/weixin/v2/notes/{}/comments?pageSize=10'.format(note_id)
    return request_query(base_api)


def extract_user_id_from_comment(note_id):
    rsp = request_comment_api(note_id)
    comment_data = None
    user_id_list = list()
    if rsp.status_code == 200:
        comment_data = json.loads(rsp.content).get('data', None)
        user_id_list += get_comment(comment_data)

    while comment_data and len(comment_data.get('comments')) == 10:
        end_id = comment_data.get('comments')[-1].get('id')
        comment_data = None
        rsp = request_comment_api(note_id, end_id)
        if rsp.status_code == 200:
            comment_data = json.loads(rsp.content).get('data', None)
            user_id_list += get_comment(comment_data)
    return user_id_list


def get_note_comment(user_id):
    user_list = list()
    note_list = get_note_list(user_id)
    for note in note_list:
        user_list += extract_user_id_from_comment(note['id'])
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

def main(partition):
    user = RedBookUser('KOL')
    user.cur.execute(f'''select distinct url,id from red_book_user partition({partition}) where is_dispatched = '0' 
    and create_time < '2022-01-08 00:00:00' ''')
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
    thread_pool = list()
    for p in [
        'p0',
        'p1', 'p2', 'p3', 'p4'
    ]:
        thread_pool.append(threading.Thread(target=main, args=(p,)))
    print("启动线程")
    for thread in thread_pool:
        thread.start()
    # start_time = time()
    for thread in thread_pool:
        thread.join()

    print("执行结束")
