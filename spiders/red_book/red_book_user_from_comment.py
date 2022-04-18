#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2022/1/23 11:33
# @Author  : v_shxliu
# @File    : red_book_user_from_comment.py
import json
import threading

from common.utils import RedBookDownloader
from spiders.red_book.redbook_user_info import RedBookUser


class ExtractorComment(RedBookDownloader):
    def get_note_list(self, user_id):
        note_item_list = list()
        page = 0

        while True:
            page += 1
            base_api = '/fe_api/burdock/weixin/v2/user/{}/notes?page={}'.format(user_id, page)
            notes_rsp = self.req_download(base_api)
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

    def process(self, user_id):
        user_list = list()
        note_list = self.get_note_list(user_id)
        for note in note_list:
            user_list += self.extract_user_id_from_comment(note['id'])
        user_list = [user['id'] for user in user_list if user['id'] != user_id]
        return set(user_list)

    @staticmethod
    def get_comment(comment_data):
        comment_list = list()
        if comment_data and comment_data.get('comments'):
            for comment in comment_data.get('comments'):
                comment_list.append(comment['user'])
                for sub_comment in comment['subComments']:
                    comment_list.append(sub_comment['user'])
        return comment_list

    def request_comment_api(self, note_id, end_id=None):
        if end_id:
            base_api = '/fe_api/burdock/weixin/v2/notes/{}/comments?pageSize=10&endId={}'.format(note_id, end_id)
        else:
            base_api = '/fe_api/burdock/weixin/v2/notes/{}/comments?pageSize=10'.format(note_id)
        return self.req_download(base_api)

    def extract_user_id_from_comment(self, note_id):
        rsp = self.request_comment_api(note_id)
        comment_data = None
        user_id_list = list()
        if rsp.status_code == 200:
            comment_data = json.loads(rsp.content).get('data', None)
            user_id_list += self.get_comment(comment_data)

        while comment_data and len(comment_data.get('comments')) == 10:
            end_id = comment_data.get('comments')[-1].get('id')
            comment_data = None
            rsp = self.request_comment_api(note_id, end_id)
            if rsp.status_code == 200:
                comment_data = json.loads(rsp.content).get('data', None)
                user_id_list += self.get_comment(comment_data)
        return user_id_list


def main(partition):
    user = RedBookUser('KOL', partition)
    user.cur.execute(f'''select distinct url,id from red_book_user partition({partition}) where is_dispatched = '0' 
    and create_time < '2022-01-08 00:00:00' ''')
    user_urls = user.cur.fetchall()
    for user_url in user_urls:
        uid = user_url[0].replace('https://www.xiaohongshu.com/user/profile/', '')
        user_id_list = ExtractorComment(partition).process(uid)
        for comment_user_id in user_id_list:
            user.parse(comment_user_id)
        sql = '''update `red_book_user` set `is_dispatched` = '1' where `id` = '{}' '''.format(user_url[1])
        user.cur.execute(sql)
        user.conn.commit()


if __name__ == '__main__':
    thread_pool = list()
    for p in [
        'p0','p1','p2'
        # 'p3', 'p4'
    ]:
        thread_pool.append(threading.Thread(target=main, args=(p,)))
    print("启动线程")
    for thread in thread_pool:
        thread.start()
    for thread in thread_pool:
        thread.join()

    print("执行结束")
