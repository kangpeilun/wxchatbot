# -*- coding: utf-8 -*-
#        Data: 2024/3/20 13:42
#     Project: wxchatbot
#   File Name: keywords.py
#      Author: KangPeilun
#       Email: 374774222@qq.com 
# Description: 手动添加Keyword，用于机器人自动回复
"""json格式：
{
    "keyword1": {
        "reply": xxx,  # 关键词的回复内容
        "reply_type": xxx  # 回复内容的类型，文本text，图片image，文件file
    }
    "keyword2": {
        "reply": xxx,
        "reply_type": xxx
    }
    ...
}
"""

import json
import os.path as op

from utils.data import database
from utils.util import *



# 以下为数据库操作
def create_keywords_to_db(keywords: dict):
    """将关键字写入数据库"""
    cursor = database.cursor()
    for idx, (keyword, reply, reply_type) in enumerate(keywords):
        cursor.execute("insert into keywords (id, keyword, reply, reply_type) "
                       f"values (keywords_seq.nextval, '{keyword}', '{reply}', '{reply_type}')")
    database.commit()

def input_keywords_to_db():
    keywords = []
    reply_type_dict = {
        '1': 'text',
        '2': 'image',
        '3': 'file'
    }
    while True:
        keyword = input(f"请输入{red_text('关键词')}(输入q退出): ")
        if keyword == "q":
            break
        reply = input(f"请输入{green_text('回复内容')}: ")
        reply_type = input(f"请输入{green_text('回复类型 <1:文本, 2:图片, 3:文件>')}: ")

        keywords.append((keyword, reply, reply_type_dict[reply_type]))
    create_keywords_to_db(keywords)
    print("关键词列表创建成功")

def read_keywords_from_db():
    """从数据库读取关键词"""
    cursor = database.cursor()
    cursor.execute("select RTRIM(keyword), RTRIM(reply), RTRIM(reply_type) from keywords")
    keywords = [(keyword[0], keyword[1].read(), keyword[2]) for keyword in cursor.fetchall()]
    if keywords == []:
        print("检测到还未创建关键词列表，请进行创建！！！")
        input_keywords_to_db()
        cursor.execute("select RTRIM(keyword), RTRIM(reply), RTRIM(reply_type) from keywords")
        keywords = [(keyword[0], keyword[1].read(), keyword[2]) for keyword in cursor.fetchall()]
    else:
        print(f"检测到已创建关键词列表，输出keywords:  {keywords}")
    return keywords

def check_keywords_from_db():
    """检测数据库中是否存在关键词"""
    cursor = database.cursor()
    cursor.execute("select RTRIM(keyword), RTRIM(reply), RTRIM(reply_type) from keywords")
    keywords = [(keyword[0], keyword[1].read(), keyword[2]) for keyword in cursor.fetchall()]  # 通过reply.read()来读取CLOB格式的字段
    if keywords == []:
        print("检测到还未创建关键词列表，请进行创建！！！")
        input_keywords_to_db()
    else:
        print(f"检测到已创建关键词列表，输出keywords:  {keywords}")


if __name__ == '__main__':
    check_keywords_from_db()
    # read_keywords_from_db()
    # input_keywords_to_db()