# -*- coding: utf-8 -*-
#        Data: 2024/3/20 11:36
#     Project: wxchatbot
#   File Name: wxchatbot.py
#      Author: KangPeilun
#       Email: 374774222@qq.com 
# Description:
"""功能需求：
1.能向微信群推送消息，如图片，文字，链接
2.客户在微信群 @助手，助手收到问题会推送给后台人员进行回答
3.捕捉诉求和敏感词，群助手可应答，能生成工单
4.提供助手运营情况分析，微信群覆盖率，建设情况，一次答复率，网络经理处理率等
5.提供诉求内容，诉求数量，诉求客户、分布区域等报表（分布区域应该难以获取）
6.能够定时，定期向群里发送通知信息
"""

import os.path as op
from wxauto import WeChat
import re
import json

from utils.listen_list import read_listen_list_from_db, check_listen_list_from_db
from utils.keywords import read_keywords_from_db, check_keywords_from_db
from utils.chat_info import insert_chat_info_to_db, get_all_chat_info, search_chat_info_by_user_group
from utils.util import *
from bot_param import Bot_param


class WxChatBot:
    def __init__(self):
        self.wx = WeChat()  # 实例化为微信对象
        check_listen_list_from_db()  # 运行前检查是否缺少文件
        check_keywords_from_db()
        self.listen_list = read_listen_list_from_db()  # 从json文件中获取监听对象名称
        self.keywords = read_keywords_from_db()  # 从json文件中获取关键词
        self.Add_Listen_Group()  # 添加需要监听的群聊

    def Add_Listen_Group(self):
        """添加需要监听的微信群
        :param group_name: str 微信群名称
        """
        for idx, listen_name in enumerate(self.listen_list):
            self.wx.AddListenChat(who=listen_name, savepic=True)
            print(f"{idx+1}. 已将群聊 {listen_name} 加入监听列表")

    def SendText(self, msg: str, listen_name: str):
        """1.向监听的微信群依次推送文字消息
        :param msg: str 文字消息
        :param listen_name: str 监听对象名称
        """
        print(f"正在向监听对象 {listen_name} 发送消息:  {msg}")
        self.wx.SendMsg(msg, who=listen_name)

    def SendFile(self, file: str, listen_name: str):
        """1.向监听的微信群推送文件消息
        :param file: str 文件路径
        :param listen_name: str 监听对象名称
        """
        print(f"正在向监听对象 {listen_name} 发送文件:  {file}")
        self.wx.SendFiles(file, who=listen_name)

    def Listen_Sensitive(self):
        """2、3.监听群组中用户的敏感词，获取到会自动回答问题"""
        print("开始监听群组中用户的关键词")
        time_count = 0  # 对扫描监听对象消息的时间间隔进行记录
        while True:
            msgs = self.wx.GetListenMessage()  # 每隔n秒对所有监测窗口扫一遍，获取该时间段内所有监听对象的新消息
            """pywintypes.error: (1400, 'SetWindowPos', '无效的窗口句柄。')
            使用self.wx.GetListenMessage()会自动打开所有监听对象的微信窗口，之后这些窗口就不能再手动关闭，
            否则就会出现上面的错误
            """
            print("time_count: ", time_count, "s\t", "msgs: ", msgs)
            #  {<wxauto Chat Window at 0x2b4693fdc70 for bot测试>: [['Time', '13:56', '42111807046638'], ['Self', '你好', '42111807046630'], ['SYS', '以下为新消息', '42111807046639'], ['微信小号', '你好', '42111807046633']]}
            if msgs != dict():
                msgs_key, msgs_value = list(msgs.keys())[0], \
                    [value for value in list(msgs.values())[0] if value[0] not in Bot_param['user_name_skip_word']]  # 跳过非用户列表
                print(msgs_key, msgs_value)
                matches = re.findall(Bot_param['group_pattern'], str(msgs_key))
                user_group =matches[0]    # 获取Bot所在群组，注意在群聊中，bot应该将消息发回群组名中
                for idx, msg in enumerate(msgs_value):
                    print("msg: ", msg)   # 输出当前时间段内所有用户的消息 ['Self', '我', '42498365841995']
                    user_name = msg[0]    # 获取当前群组下发送消息的用户的用户名
                    user_text = msg[1]    # 获取用户发送的文本

                    for keyword, reply, reply_type in self.keywords:
                        if keyword in user_text:  # 循环检测用户输入是否含有关键词，然后发送对应消息
                            if reply_type == 'image' or reply_type == 'file':
                                self.SendFile(reply, user_group)
                            else:
                                self.SendText(reply, user_group)
                            insert_chat_info_to_db(user_name, user_group, user_text, reply, reply_type)
                            break
                    time_count += Bot_param['bot_reply_wait_time']  # 计算Bot在该次间隔内回答所有问题所用时间
                    time.sleep(Bot_param['bot_reply_wait_time'])
            time_count += Bot_param['listen_wait_time']  # 计算每次Bot响应的总时间间隔
            time.sleep(Bot_param['listen_wait_time'])

    def Create_Analysis_Report(self, report_path='./report.txt'):
        """4.提供助手运营情况分析，微信群覆盖率，建设情况，一次答复率，网络经理处理率等
                1.记录哪些群聊在使用Bot
                2.Bot每在向群里发送一次消息就记为一次答复
                3.记录Bot每次响应时与用户对话内容，以及客户名称
        :param report_path: 报告存放的路径
        """
        listen_user_dict = {}
        group_use_Bot = set()  # 使用集合记录，哪些群组使用过Bot
        user_use_Bot = set()   # 哪些用户使用过Bot
        all_chat_times = 0  # 所有对话的次数
        for idx, listen_name in enumerate(self.listen_list):
            user_chat_info_all = search_chat_info_by_user_group(listen_name)  # 获取监听对象所有的对话记录
            # ic(user_chat_info_all)
            all_chat_times += len(user_chat_info_all)
            if user_chat_info_all == []:  # 如果为空，就跳过当前用户
                continue
            for user_chat_info in user_chat_info_all:  # 用户每条对话记录
                if listen_name not in listen_user_dict:
                    listen_user_dict[listen_name] = []
                one_user_chat_info_record = {
                    'user_name': user_chat_info[0],
                    'user_group': user_chat_info[1],  # 正常来讲，如果Bot只存在于群聊当中，那么监听对象listen_name和用户所在群组user_group是相等的，如果聊天对象为个人，那么listen_name==user_name
                    'user_text': user_chat_info[2],
                    'reply': user_chat_info[3],
                    'time': user_chat_info[4],
                    'reply_type': user_chat_info[5]
                }
                listen_user_dict[listen_name].append(one_user_chat_info_record)
                user_use_Bot.add(one_user_chat_info_record['user_name'])
            group_use_Bot.add(listen_name)

        # 将所有监听对象的对话记录存入json文件
        json_path = op.join(op.dirname(report_path), "user_chat_info.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(listen_user_dict, f, ensure_ascii=False, indent=4)

        # 开始对对话记录进行分析
        report_str = """
        对话记录分析报告: \n
        在本次运行过程中共监测到{}个用户使用了Bot，且共有{}个群聊拥有Bot，这些群组分别为: \n
        其中Bot和用户{}进行了{}次对话，该用户所在群组为{}，对话内容如下: \n
        """
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("对话记录分析报告: \n")
            report_str1 = f"在本次运行过程中共监测到{len(user_use_Bot)}个群组使用了Bot，一共进行了{all_chat_times}次对话，这些群组分别为: \n"
            for group in group_use_Bot:
                report_str1 += f"{group}\n"
            f.write(report_str1)

            # 正常来讲，如果Bot只存在于群聊当中，那么监听对象listen_name和用户所在群组user_group是相等的，如果聊天对象为个人，那么listen_name==user_name
            for listen_name, chat_info in listen_user_dict.items():
                report_str2 = f"\n在群组 {listen_name} 中，Bot进行了{len(chat_info)}次对话，对话内容如下: \n"
                for chat_record in chat_info:
                    report_str2 += f"{chat_record['user_name']}\t user_text: {chat_record['user_text']}\t reply: {chat_record['reply']}\t [{chat_record['time']}]\n"
                f.write(report_str2)

        print(f"报告以生成，请打开文件 {report_path} 查看")


if __name__ == '__main__':
    # log_file = save_log()
    Bot = WxChatBot()
    # Bot.SendText_Group("你好，我是小助手，有什么可以帮助你的吗？")
    # Bot.SendFile_Group(r"D:\UserData\Pictures\Saved Pictures\美图\wallhaven-6d56k6.jpg")
    Bot.Listen_Sensitive()
    # log_file.close()
    # Bot.Create_Analysis_Report()
