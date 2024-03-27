# -*- coding: utf-8 -*-
#        Data: 2024-03-27 18:13
#     Project: wxchatbot
#   File Name: service_user_chat.py
#      Author: KangPeilun
#       Email: 374774222@qq.com 
# Description: 记录客服与用户的对话内容
"""
{
    id: id
    user_name: 用户1
    user_group: 群组1
    service_name: 客服1
    user_question: 问题1
    service_reply: 客服回答1
    time: 时间
}
"""

from utils.util import *
from utils.database import database


def insert_service_user_chat_to_db(user_name, user_group, user_question, service_name, service_reply):
    """将客服与用户的对话内容插入数据库"""
    cursor = database.cursor()
    cursor.execute(f"insert into service_user_chat (id, user_name, user_group, user_question, service_name, service_reply) values (service_user_chat_seq.nextval, '{user_name}', '{user_group}', '{user_question}', '{service_name}', '{service_reply}')")
    database.commit()

