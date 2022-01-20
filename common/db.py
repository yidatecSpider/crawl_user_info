#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/6 17:03
# @Author  : v_shxliu
# @File    : db.py
import pymysql

from common.hashlib_get_id import get_raw_video_id


class DBHelper:

    def __init__(self, host="127.0.0.1", port=3306, user="root", password="pass",
                 database="spider"):  # 构造函数
        try:
            self.conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database,
                                        charset='utf8')
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(e)

    # 返回执行execute()方法后影响的行数

    def execute(self, sql):
        self.cursor.execute(sql)
        rowcount = self.cursor.rowcount
        return rowcount

    # 删除并返回影响行数
    def delete(self, **kwargs):
        table = kwargs['table']

        where = kwargs['where']
        sql = 'DELETE FROM %s where %s' % (table, where)
        print(sql)
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 提交到数据库执行
            self.conn.commit()
            # 影响的行数
            rowcount = self.cursor.rowcount
        except:
            # 发生错误时回滚
            self.conn.rollback()
        return rowcount

    # 新增并返回新增ID
    def insert(self, **kwargs):
        table = kwargs['table']
        del kwargs['table']
        sql = 'insert into %s(' % table
        fields = ""
        values = ""
        for k, v in kwargs.items():
            fields += "%s," % k
            values += "'%s'," % v
        fields = fields.rstrip(',')
        values = values.rstrip(',')
        sql = sql + fields + ")values(" + values + ")"
        print(sql)
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 提交到数据库执行
            self.conn.commit()
            # 获取自增id
            res = self.cursor.lastrowid
        except:
            # 发生错误时回滚
            self.conn.rollback()
        return res

    # 修改数据并返回影响的行数

    def update(self, **kwargs):
        table = kwargs['table']
        # del kwargs['table']
        kwargs.pop('table')
        where = kwargs['where']
        kwargs.pop('where')
        sql = 'update %s set ' % table
        for k, v in kwargs.items():
            sql += "%s='%s'," % (k, v)
        sql = sql.rstrip(',')
        sql += ' where %s' % where
        print(sql)
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 提交到数据库执行
            self.conn.commit()
            # 影响的行数
            rowcount = self.cursor.rowcount
        except Exception as e:
            # 发生错误时回滚
            self.conn.rollback()
        return rowcount

    # 查-一条条数据
    def selectTopone(self, **kwargs):
        table = kwargs['table']
        field = 'field' in kwargs and kwargs['field'] or '*'
        where = 'where' in kwargs and 'where ' + kwargs['where'] or ''
        order = 'order' in kwargs and 'order by ' + kwargs['order'] or ''
        sql = 'select %s from %s %s %s limit 1' % (field, table, where, order)
        print(sql)
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 使用 fetchone() 方法获取单条数据.
            data = self.cursor.fetchone()
        except:
            # 发生错误时回滚
            self.conn.rollback()
        return data

    # 查所有数据
    def select_all(self, **kwargs):
        result = list()
        table = kwargs['table']
        field = 'field' in kwargs and kwargs['field'] or '*'
        where = 'where' in kwargs and 'where ' + kwargs['where'] or ''
        order = 'order' in kwargs and 'order by ' + kwargs['order'] or ''
        limit = 'limit' in kwargs and 'limit ' + kwargs['limit'] or ''
        sql = 'select %s from %s %s %s %s ' % (field, table, where, order, limit)
        print(sql)
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 使用 fetchone() 方法获取单条数据.
            result = self.cursor.fetchall()
        except:
            # 发生错误时回滚
            self.conn.rollback()
        return result


if __name__ == '__main__':
    db = DBHelper()
    data = db.select_all(table='red_book_user')
    start = 0
    batch_num = 1000
    sql = '''update red_book_user set hash_code = %s where id = %s '''
    time = len(data) // batch_num + 1 if len(data) % batch_num != 0 else len(data) // batch_num
    for i in range(time):
        insert_data = list()
        for user_info in data[i * batch_num:(i + 1) * batch_num]:
            uid = user_info[0].replace('https://www.xiaohongshu.com/user/profile/', '')
            hash_code = get_raw_video_id(uid)
            insert_data.append([hash_code, user_info[0]])
        print(insert_data)
        exec_re = db.cursor.executemany(sql, insert_data)
        db.conn.commit()
        pass
