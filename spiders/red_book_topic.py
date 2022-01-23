#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/8/20 10:50
# @Author  : v_shxliu
# @File    : xiaohongshu.py
import json
import re
from urllib.parse import quote
import requests
from time import sleep, time, strftime, localtime
from common import sign
from spiders.redbook_user_info import RedBookUser
import random

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


def main():
    user = RedBookUser('KOL')
    user_id_list = extract_user_list()
    for user_id in user_id_list:
        sleep(round(random.uniform(2, 5), 1))
        user.parse(user_id)


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
