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
import time
from datetime import datetime

from wxauto import WeChat
import re
import json

from utils.listen_list import read_listen_list_from_db, check_listen_list_from_db
from utils.keywords import read_keywords_from_db, check_keywords_from_db
from utils.bot_service import read_bot_service_from_db, check_bot_service_from_db
from utils.bot_chat_info import insert_bot_chat_info_to_db, get_all_bot_chat_info, search_bot_chat_info_by_user_group
from utils.service_user_chat import insert_service_user_chat_to_db
from utils.all_msg import insert_all_msg_to_db
from utils.util import *
from bot_param import Bot_param


class WxChatBot:
    def __init__(self):
        self.wx = WeChat()                                  # 实例化为微信对象
        self.Bot_name = self.wx.nickname                    # 获取Bot名称
        # 启动前参数初始化，以及数据检查
        check_listen_list_from_db()                         # 检查是否添加监听列表
        check_keywords_from_db()                            # 检查是否添加关键词列表
        check_bot_service_from_db()                         # 检查是否添加bot和客服对应表
        self.listen_list = read_listen_list_from_db()       # 从db中获取监听对象名称 list
        self.keywords = read_keywords_from_db()             # 从db中获取关键词 list
        self.bot_service = read_bot_service_from_db()       # 从db中获取bot和客服对应表，dict
        self.service = self.bot_service[self.Bot_name]      # 获取该Bot对应的客服名称
        self.__Add_Listen_Group()                           # 添加需要监听的群聊
        # Bot正式启动，并开始记录时间
        self.__Bot_Boot_output_msg()

    def __Bot_Boot_output_msg(self):
        """Bot启动的输出信息, 用于记录一些Bot运行时的一些信息，比如运行时间，消息提示
        Time格式: 时间戳 精确到秒
        """
        print(red_text("Bot初始化完成，并完成启动，持续收集群聊信息，并监听用户关键词..."))
        self.start_time = int(time.time())                  # 获取时间戳，方便计时，精确到秒
        self.start_time_format = datetime.fromtimestamp(self.start_time).strftime("%Y-%m-%d %H:%M:%S")

    def __Bot_wait_time(self, wait_time):
        """用于Bot回答问题的缓冲时间，防止回答过快导致微信退出"""
        time.sleep(wait_time)

    def __get_time(self):
        """用于获取系统当前时间，时间戳，精确到秒"""
        now_time = int(time.time())                         # 获取当前时间
        time_spend = now_time - self.start_time             # 获取距离Bot启动过去了多少秒
        now_time_format = datetime.fromtimestamp(now_time).strftime("%Y-%m-%d %H:%M:%S")
        return now_time, now_time_format, time_spend

    def __Add_Listen_Group(self):
        """添加需要监听的微信群
        :param group_name: str 微信群名称
        """
        for idx, listen_name in enumerate(self.listen_list):
            self.wx.AddListenChat(who=listen_name, savepic=True)
            print(f"{idx+1}. 已将群聊 {listen_name} 加入监听列表")

    def __SendText(self, msg: str, listen_name: str):
        """1.向监听的微信群依次推送文字消息
        :param msg: str 文字消息
        :param listen_name: str 监听对象名称
        """
        print(f"正在向监听对象 {listen_name} 发送消息:  {msg}")
        self.wx.SendMsg(msg, who=listen_name)

    def __SendFile(self, file: str, listen_name: str):
        """1.向监听的微信群推送文件消息
        :param file: str 文件路径
        :param listen_name: str 监听对象名称
        """
        print(f"正在向监听对象 {listen_name} 发送文件:  {file}")
        self.wx.SendFiles(file, who=listen_name)

    def __Listen_Sensitive(self):
        """Bot时刻监听群组中用户的对话内容，并根据监测到的关键词发送提前准备好的自动回复内容"""
        # time_count = 0  # 对扫描监听对象消息的时间间隔进行记录
        msgs = self.wx.GetListenMessage()  # 每隔n秒对所有监测窗口扫一遍，获取该时间段内所有监听对象的新消息
        """pywintypes.error: (1400, 'SetWindowPos', '无效的窗口句柄。')
        使用self.wx.GetListenMessage()会自动打开所有监听对象的微信窗口，之后这些窗口就不能再手动关闭，
        否则就会出现上面的错误
        """
        print("time_count: ", self.__get_time()[2], "s\t", "msgs: ", msgs)
        #  {<wxauto Chat Window at 0x2b4693fdc70 for bot测试>: [['Time', '13:56', '42111807046638'], ['Self', '你好', '42111807046630'], ['SYS', '以下为新消息', '42111807046639'], ['微信小号', '你好', '42111807046633']]}
        if msgs != {}:
            for msg_key, msg_value in msgs.items():
                msg_value = [value for value in msg_value if value[0] not in Bot_param['user_name_skip_word']]  # 跳过非用户列表
                print(msg_key, msg_value)
                matches = re.findall(Bot_param['group_pattern'], str(msg_key))
                user_group =matches[0]    # 获取Bot所在群组，注意在群聊中，bot应该将消息发回群组名中
                for idx, msg in enumerate(msg_value):  # 当msg_value为空时，for循环不执行
                    print("msg: ", msg)   # 输出当前时间段内所有用户的消息 ['Self', '我', '42498365841995']
                    user_name = msg[0]    # 获取当前群组下发送消息的用户的用户名
                    user_text = msg[1]    # 获取用户发送的文本

                    if f"@{self.Bot_name}" in user_text:
                        # 用户的输入文本中含有 '@Bot' 字样，选择进入特定任务进行处理，否则维持一般监测状态，检测到关键词就自动发送回复
                        # 指令用于控制Bot要去做一件什么事，设定的指令有：问题，时间，报告
                        # 动作表示用户期望Bot完成的任务，如：设定定时消息，向Bot对应客服发送消息
                        try:  # try解决python无法分割出指定数量的元素的问题
                            # 尝试对用户的输入进行分割，如果无法按照正确的格式分割，Bot就提示用户指令是否输入正确
                            user_text = user_text.replace("\u2005", " ")
                            _, instruct, action = user_text.split(Bot_param["instruct_split_symbol"], 2)  # 使用空格将用户的输入进行分割，["@Bot", "指令", "动作"]
                            if instruct == "问题":
                                self.__SendText(Bot_param["hold_on_msg"], user_group)
                                self.__Bot_wait_time(Bot_param['bot_reply_wait_time'])  # 控制Bot回复等待时间，防止回复过快，微信掉线
                                self.__Listen_Question(user_name, user_group, action)  # 向Bot对应客服发送消息
                                self.__Bot_wait_time(Bot_param['bot_reply_wait_time'])  # 控制Bot回复等待时间，防止回复过快，微信掉线
                            elif instruct == "时间":
                                pass
                            elif instruct == "报告":
                                pass
                            else:  # else解决用户输入没有关键词的问题
                                # 提示用户指令是否输入错误？
                                self.__SendText(Bot_param["remind_instruct_msg"], user_group)
                                self.__Bot_wait_time(Bot_param['bot_reply_wait_time'])  # 控制Bot回复等待时间，防止回复过快，微信掉线
                        except:
                            # 提示用户指令是否输入错误？
                            self.__SendText(Bot_param["remind_instruct_msg"], user_group)
                            self.__Bot_wait_time(Bot_param['bot_reply_wait_time'])  # 控制Bot回复等待时间，防止回复过快，微信掉线

                    else:  # 否则维持一般监测状态，检测到关键词就自动发送回复
                        for keyword, reply, reply_type in self.keywords:
                            if keyword in user_text:  # 循环检测用户输入是否含有关键词，然后发送对应消息
                                if reply_type == 'image' or reply_type == 'file':
                                    self.__SendFile(reply, user_group)
                                else:
                                    self.__SendText(reply, user_group)
                                insert_bot_chat_info_to_db(user_name, user_group, user_text, reply, reply_type)
                                break

                    print(f"正在收集Bot启动时间{green_text(self.start_time_format)}至当前时间{red_text(self.__get_time()[1])}的所有群聊消息")
                    self.__Collect_All_User_Msg(user_name, user_group, user_text)
                    self.__Bot_wait_time(Bot_param['bot_reply_wait_time'])  # Bot依次回答每个关键词的间隔时间

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
            user_bot_chat_info_all = search_bot_chat_info_by_user_group(listen_name)  # 获取监听对象所有的对话记录
            # ic(user_bot_chat_info_all)
            all_chat_times += len(user_bot_chat_info_all)
            if user_bot_chat_info_all == []:  # 如果为空，就跳过当前用户
                continue
            for user_bot_chat_info in user_bot_chat_info_all:  # 用户每条对话记录
                if listen_name not in listen_user_dict:
                    listen_user_dict[listen_name] = []
                one_user_bot_chat_info_record = {
                    'user_name': user_bot_chat_info[0],
                    'user_group': user_bot_chat_info[1],  # 正常来讲，如果Bot只存在于群聊当中，那么监听对象listen_name和用户所在群组user_group是相等的，如果聊天对象为个人，那么listen_name==user_name
                    'user_text': user_bot_chat_info[2],
                    'reply': user_bot_chat_info[3],
                    'time': user_bot_chat_info[4],
                    'reply_type': user_bot_chat_info[5]
                }
                listen_user_dict[listen_name].append(one_user_bot_chat_info_record)
                user_use_Bot.add(one_user_bot_chat_info_record['user_name'])
            group_use_Bot.add(listen_name)

        # 将所有监听对象的对话记录存入json文件
        json_path = op.join(op.dirname(report_path), "user_bot_chat_info.json")
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
            for listen_name, bot_chat_info in listen_user_dict.items():
                report_str2 = f"\n在群组 {listen_name} 中，Bot进行了{len(bot_chat_info)}次对话，对话内容如下: \n"
                for chat_record in bot_chat_info:
                    report_str2 += f"{chat_record['user_name']}\t user_text: {chat_record['user_text']}\t reply: {chat_record['reply']}\t [{chat_record['time']}]\n"
                f.write(report_str2)

        print(f"报告以生成，请打开文件 {report_path} 查看")


    def __Listen_Report(self):
        """监听
        '@Bot 报告'
        用于报告的打印, 并发送给管理员用户的个人账户
        同时Bot发送类似正在执行的提示信息
        """
        pass

    def __Listen_Time(self):
        """监听
        '@Bot 时间 待发送的消息A'
        用于在指定时间将A发送给所有群组
        同时Bot发送类似正在执行的提示信息
        """
        pass

    def __Listen_Question(self, user_name, user_group, action):
        """Bot要和客服是微信好友才能实现，service为Bot给客服备注的名称
        监听
        '@Bot 问题 问题本身A'
        Bot将问题发送给其对应的客服微信，同时附带群聊名称，以及用户名称，方便客服与用户对接
        同时Bot发送类似正在执行的提示信息
        """
        print(f"正在向客服 {self.service} 发送来自群组 {user_group}, 用户为 {user_name} 的问题")
        msg_body = f"来自下面的群组的用户发送过来一个问题，请及时处理\n群组：{user_group}\n用户：{user_name}\n问题：{action}"
        self.wx.SendMsg(msg_body, who=self.service)
        insert_service_user_chat_to_db(user_name, user_group, action, self.service)  # 将用户的问题，以及其相关信息填入数据库


    def __Collect_All_User_Msg(self, user_name, user_group, user_text):
        """Bot每隔一段时间收集监听群组中所有用户发送的消息，将文字存入数据库，文件存入指定文件夹内
        数据库字段：id user_name group_name user_text time
        如果用户发送的是图片，则将图片存入指定文件夹内，并将图片路径存入数据库user_text字段
        """
        insert_all_msg_to_db(user_name, user_group, user_text)

    def __Send_Command_to_All_Group(self):
        """每隔一段时间，Bot向所有群组发送如何触发Bot执行命令的指令，比如：
        @Bot 问题 问题本身A
        @Bot 时间 待发送的消息A
        @Bot 报告
        """
        pass

    def Run_Bot(self):
        """在该While True循环下，Bot根据不同指令执行不同的动作"""
        while True:
            self.__Listen_Sensitive()

            self.__Bot_wait_time(Bot_param['listen_wait_time'])  # Bot每隔多久扫描一次所有群聊的消息


if __name__ == '__main__':
    # log_file = save_log()
    Bot = WxChatBot()
    # Bot.SendText_Group("你好，我是小助手，有什么可以帮助你的吗？")
    # Bot.SendFile_Group(r"D:\UserData\Pictures\Saved Pictures\美图\wallhaven-6d56k6.jpg")
    Bot.Run_Bot()
    # log_file.close()
    # Bot.Create_Analysis_Report()
