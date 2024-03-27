# -*- coding: utf-8 -*-
#        Data: 2024/3/22 12:09
#     Project: wxchatbot
#   File Name: util.py
#      Author: KangPeilun
#       Email: 374774222@qq.com 
# Description:

import sys
import time
from icecream import ic

green_text = lambda text: f"\033[32m{text}\033[0m"  # 给文本添加绿色，方便查看
red_text = lambda text: f"\033[31m{text}\033[0m"    # 给文本添加红色
timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
ic.configureOutput(prefix=f"[{timestamp}] ")

def save_log():
    log_file = open("./log.txt", "a", encoding="utf-8")
    sys.stdout = log_file
    return log_file



if __name__ == '__main__':

    ic("hello", 1312312, [1234123123])