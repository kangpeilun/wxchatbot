# -*- coding: utf-8 -*-
#        Data: 2024/3/20 15:30
#     Project: wxchatbot
#   File Name: database.py
#      Author: KangPeilun
#       Email: 374774222@qq.com 
# Description:

import cx_Oracle

database_param = {
    "user": 'scott',
    "password": '253325',
    "host": '127.0.0.1:1521',
    "database": 'orcl'
}

conn_str = f"{database_param['user']}/{database_param['password']}@{database_param['host']}/{database_param['database']}"
database = cx_Oracle.connect(conn_str)


# cursor = database.cursor()
# cursor.execute('select * from chat_info')
# print(cursor.fetchall())
