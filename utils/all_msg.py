# -*- coding: utf-8 -*-
#        Data: 2024-03-27 18:38
#     Project: wxchatbot
#   File Name: all_msg.py
#      Author: KangPeilun
#       Email: 374774222@qq.com 
# Description: 记录所有被监听的群组的所有聊天内容
"""
{
    id: id
    user_name: 用户名1
    user_group: 群组1
    user_text: 用户消息1
    time: 时间
}
"""


from utils.util import *
from utils.database import database


def insert_all_msg_to_db(user_name, user_group, user_text):
    """将所有被监听的群组的所有聊天内容插入数据库"""
    cursor = database.cursor()
    cursor.execute(f"insert into all_msg (id, user_name, user_group, user_text) values (all_msg_seq.nextval, '{user_name}', '{user_group}', '{user_text}')")
    database.commit()