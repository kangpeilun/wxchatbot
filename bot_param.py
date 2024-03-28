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
    "user_name_skip_word": ["SYS", "Time", "Self"],  # 跳过无意义的用户名称，Self表示Bot自身，一般自己不和自己对话，删除Self仅用于Debug
    # "user_name_skip_word": ["SYS", "Time"],  # 删除Self仅用于Debug
    "hold_on_msg": f"尊敬的客户，请您稍等，会有专属人员为您服务！",  # 客户在@Bot，并向人工客服提出问题时，Bot回复让客户稍等的消息
    "instruct_split_symbol": " ",  # 使用空格分割，用于分割用户指令的分隔符，如用户发送：'@Bot 问题 问题本身'，Bot将用户的输入分割成list=['@Bot', '问题', '问题本身']三部分
    "remind_instruct_msg": f"请检查您输入的指令是否正确，若要向人工客服提问题请发送：\n"
                           "@电力小哥 问题(空格)您的问题"  # 用户在输入错指令后，Bot提醒用户输入正确指令的语句
}