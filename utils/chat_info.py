# -*- coding: utf-8 -*-
#        Data: 2024/3/20 16:19
#     Project: wxchatbot
#   File Name: chat_info.py
#      Author: KangPeilun
#       Email: 374774222@qq.com 
# Description: 创建json文件记录Bot与所有用户的每条对话信息
"""json格式：
{
    "user_name": [
            {
                "time": xxx,   # 对话时间
                "group": xxx,  # 用户所在聊天群
                "user_text": xxx, # 用户输入的文本
                "reply": xxx,  # Bot回答
                "reply_type": xxx,  # reply的类型，文本，图片，文件
            },
            {
                "time": xxx,
                "group": xxx,
                "user_text": xxx,
                "reply": xxx,
                "reply_type": xxx,
            },
            ...
        ]
}
"""

from utils.util import *
from utils.data import database


def insert_chat_info_to_db(user_name, user_group, user_text, reply, reply_type):
    """将对话信息插入数据库"""
    cursor = database.cursor()
    cursor.execute("insert into chat_info (id, user_name, user_group, user_text, reply, reply_type) "
                   f"values (chat_info_seq.nextval, '{user_name}', '{user_group}', '{user_text}', '{reply}', '{reply_type}')")
    database.commit()


def search_chat_info_by_user_group(user_group):
    """从数据库中获取对话信息"""
    cursor = database.cursor()
    cursor.execute(f"select RTRIM(user_name), RTRIM(user_group), RTRIM(user_text), RTRIM(reply), RTRIM(time), RTRIM(reply_type) "
                   f"from chat_info where user_group = '{user_group}'")
    chat_info = [(chat[0], chat[1], chat[2].read(), chat[3].read(), chat[4], chat[5]) for chat in cursor.fetchall()]
    return chat_info


def search_chat_info_by_condition(condition):
    """自定义查询规则，从chat_info中查询相应数据
    :param condition: 查询条件，e.g. condition: "user_name = 'xxx'",
                        condition: "user_name = 'xxx' and group = 'xxx'"
    """

    cursor = database.cursor()
    cursor.execute("select RTRIM(user_name), RTRIM(user_group), RTRIM(user_text), RTRIM(reply), RTRIM(time), RTRIM(reply_type) "
                   f"from chat_info where {condition}")
    chat_info = [(chat[0], chat[1], chat[2].read(), chat[3].read(), chat[4], chat[5]) for chat in cursor.fetchall()]
    return chat_info


def get_all_chat_info():
    """从数据库中获取所有对话信息"""
    cursor = database.cursor()
    cursor.execute("SELECT RTRIM(user_name), RTRIM(user_group), RTRIM(user_text), RTRIM(reply), RTRIM(time), RTRIM(reply_type) FROM chat_info")
    chat_info = [(chat[0], chat[1], chat[2].read(), chat[3].read(), chat[4], chat[5]) for chat in cursor.fetchall()]
    print(f"输出所有对话记录: ", chat_info)
    return chat_info


if __name__ == '__main__':
    get_all_chat_info()