# -*- coding: utf-8 -*-
#        Data: 2024-03-27 14:09
#     Project: wxchatbot
#   File Name: bot_service.py
#      Author: KangPeilun
#       Email: 374774222@qq.com 
# Description: 用于Bot和客服进行对接
"""
{
    "bot1": 客服1,
    "bot2": 客服2,
    "bot3": 客服3
}
"""

from utils.util import *
from utils.database import database

def create_bot_service_to_db(bot_service_list):
    """创建 Bot和客服对应表
    Bot1: 客服1
    Bot2: 客服2
    用于Bot找到自身的客服进行对接
    """
    cursor = database.cursor()
    for bot, service in bot_service_list:
        cursor.execute(f"insert into bot_service (id, bot_name, service_name) values (bot_service_seq.nextval, '{bot}', '{service}')")
    database.commit()

def input_bot_service_to_db():
    bot_service_list = []
    while True:
        bot_name = input(f"请输入{red_text('机器人名称')}(输入q退出): ")
        if bot_name == "q":
            break
        service_name = input(f"请输入该机器人对应的{red_text('客服名称')}: ")
        bot_service_list.append((bot_name, service_name))
    create_bot_service_to_db(bot_service_list)
    print("Bot和客服对应表创建成功")


def read_bot_service_from_db():
    """读取Bot和客服对应表"""
    cursor = database.cursor()
    cursor.execute("select RTRIM(bot_name), RTRIM(service_name) from bot_service")
    bot_service_list = {bot: service for bot, service in cursor.fetchall()}
    if bot_service_list == {}:
        print("当前Bot和客服对应表为空，请先创建对应表! ! !")
        input_bot_service_to_db()
        cursor.execute("select RTRIM(bot_name), RTRIM(service_name) from bot_service")
        bot_service_list = {bot: service for bot, service in cursor.fetchall()}
    else:
        print(f"检测到已创建Bot和客服对应表，输出bot_service_list: {bot_service_list}")
    return bot_service_list

def check_bot_service_from_db():
    """检测bot_service表是否为空"""
    cursor = database.cursor()
    cursor.execute("select RTRIM(bot_name), RTRIM(service_name) from bot_service")
    bot_service_list = {bot: service for bot, service in cursor.fetchall()}
    if bot_service_list == {}:
        print("当前Bot和客服对应表为空，请先创建对应表! ! !")
        input_bot_service_to_db()
    else:
        print(f"检测到已创建Bot和客服对应表，输出bot_service_list: {bot_service_list}")



if __name__ == '__main__':
    check_bot_service_from_db()
    # read_bot_service_from_db()