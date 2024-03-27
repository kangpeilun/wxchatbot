# -*- coding: utf-8 -*-
#        Data: 2024/3/20 12:00
#     Project: wxchatbot
#   File Name: listen_list.py
#      Author: KangPeilun
#       Email: 374774222@qq.com 
# Description: 用于手动输入被监听用户名，并自动导入json文件中，供Bot监听
"""json格式：
{
    "listen_list": [xxx, xxx, ...]  # 监听对象列表
}
"""

import json
import os.path as op
from utils.util import *
from utils.data import database


# 以下为数据库操作
def create_listen_list_to_db(listen_list):
    """将信息写入数据库"""
    cursor = database.cursor()
    for idx, listen_name in enumerate(listen_list):
        cursor.execute(f"INSERT INTO listen_list (id, listen_name) VALUES (listen_list_seq.nextval, '{listen_name}')")  # 注意：如果在数据表中定义了段名为字符变量，则在插入sql时要将变量用双引号括起来
    database.commit()


def input_listen_list_to_db():
    listen_list = []
    while True:
        name = input(f"请输入{red_text('被监听用户名')}(输入q退出): ")
        if name == "q":
            break
        listen_list.append(name)
    create_listen_list_to_db(listen_list)
    print("监听列表创建成功")


def read_listen_list_from_db():
    """从数据库中读取监听列表，如果为空则进行创建"""
    cursor = database.cursor()
    cursor.execute("SELECT RTRIM(listen_name) FROM listen_list")  # 使用SELECT语句时，使用RTRIM函数去掉字符右侧的空格。
    listen_list = [listen_name[0] for listen_name in cursor.fetchall()]
    # print(listen_list)
    if listen_list == []:
        print("检测到还未创建监听列表，请进行创建！！！")
        input_listen_list_to_db()
        cursor.execute("SELECT RTRIM(listen_name) FROM listen_list")  # 使用SELECT语句时，使用RTRIM函数去掉字符右侧的空格。
        listen_list = [listen_name[0] for listen_name in cursor.fetchall()]
    else:
        print(f"检测到已创建监听列表，输出listen_list: \n {listen_list}")
    return listen_list


def check_listen_list_from_db():
    """检测listen_list文件是否存在，以及是否为空"""
    cursor = database.cursor()
    cursor.execute("select RTRIM(listen_name) from listen_list")
    listen_list = [listen_name[0] for listen_name in cursor.fetchall()]
    exist_flag = True if listen_list != [] else False

    if not exist_flag:
        print("检测到还未创建监听列表，请进行创建！！！")
        input_listen_list_to_db()
    else:
        print(f"检测到已创建监听列表，输出listen_list: \n {listen_list}")



if __name__ == '__main__':
    # input_listen_list_to_db()
    check_listen_list_from_db()
    # read_listen_list_from_db()