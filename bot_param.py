# -*- coding: utf-8 -*-
#        Data: 2024/3/21 14:42
#     Project: wxchatbot
#   File Name: bot_param.py
#      Author: KangPeilun
#       Email: 374774222@qq.com 
# Description: 机器人相关参数，根据需要进行修改

Bot_param = {
    "listen_wait_time": 10,  # 监听频率，单位s，定义每隔多久对所有监听的聊天框完全扫描一遍
    "bot_reply_wait_time": 1,  # Bot响应关键词后，回答问题的间隔时间，太短的回复间隔可能会导致Bot无法回答所有问题
    "group_pattern": r"<wxauto Chat Window at .*? for (?P<user_group>.*?)>",  # 用于正则匹配用户群组名称
    # "user_name_skip_word": ["SYS", "Time", "Self"],  # 跳过无意义的用户名称，Self表示Bot自身，一般自己不和自己对话，删除Self仅用于Debug
    "user_name_skip_word": ["SYS", "Time"],  # 删除Self仅用于Debug
}