# wxchatbot  (适用PC微信3.9.8.15版本）

Windows版本微信客户端自动化，可实现简单的发送、接收微信消息、保存聊天图片

**相关版本安装包下载**：
[OneDrive](https://1drv.ms/f/s!AqQw88ELOBiTgcAN_bBQlBaz60PTBg?e=oGoeju) |
[百度云](https://pan.baidu.com/s/1FvSw0Fk54GGvmQq8xSrNjA?pwd=vsmj)


|  环境  | 版本 |
| :----: | :--: |
|   OS   | [![Windows](https://img.shields.io/badge/Windows-10\|11\|Server2016+-white?logo=windows&logoColor=white)](https://www.microsoft.com/)  |
|  微信  | [![Wechat](https://img.shields.io/badge/%E5%BE%AE%E4%BF%A1-3.9.8.X-07c160?logo=wechat&logoColor=white)](https://weixin.qq.com/cgi-bin/readtemplate?ang=zh_CN&t=page/faq/win/335/index&faq=win_335) **(3.9.9疑似容易掉线)** |
| Python | [![Python](https://img.shields.io/badge/Python-3.X-blue?logo=python&logoColor=white)](https://www.python.org/) **(不支持3.7.6和3.8.1)**|


### 部分版本的微信可能由于UI界面不同从而无法使用，截至2023-11-20最新版本可用


## 安装wxchatbot（请勿直接pip install）
cmd窗口：
```shell
cd wxchatbot
pip install -r requirements.txt
```

# 使用方法
> 1. bot_param.py 文件中存放着控制Bot的相关参数，注释写的很详细，除了注明debug使用的外，其他的不要随便修改
>
> ![image-20240322163108425](https://typora-kpl.oss-cn-hangzhou.aliyuncs.com/image-20240322163108425.png)
>
> 2. 切记：登录在电脑上的微信作为Bot，跟微信是谁的没有关系，比如我的账号登录了微信，那么我的账号就变成了一个自动发消息的Bot，只是我的昵称没有改成Bot罢了
## 1.创建listen_list, keywords, chat_info三张表
```python
# listen_list表字段, 可以根据需求自己修改变量类型
id number # pk
listen_name varchar2(150)

# keywords表字段, 可以根据需求自己修改变量类型
id number  # pk
keyword varchar2(150)
reply clob
reply_type varchar2(10) = 'text'  # 默认值为'text'

# chat_info表字段
id number  # pk
user_name varchar2(150)
user_group varchar2(150)
user_text clob
reply clob
reply_type varchar2(10) = NULL  # 默认值为NULL
time date = SYSDATE  # 自动填充系统时间

# 同时设置了三个sequences，用于三张表的主键自增
listen_list_seq
keywords_seq
chat_info_seq
```

`在utils/data.py中配置数据库连接信息`

![image-20240322162855529](https://typora-kpl.oss-cn-hangzhou.aliyuncs.com/image-20240322162855529.png)

![image-20240322162926680](https://typora-kpl.oss-cn-hangzhou.aliyuncs.com/image-20240322162926680.png)

![image-20240322162946623](https://typora-kpl.oss-cn-hangzhou.aliyuncs.com/image-20240322162946623.png)

![image-20240322163003764](https://typora-kpl.oss-cn-hangzhou.aliyuncs.com/image-20240322163003764.png)

## 2.向listen_list表中插入监听对象(默认对象都为 群组)

1. 运行utils/listen_list.py文件里的check_listen_list_from_db()函数，向listen_list表中插入监听对象，根据提示进行操作即可

![image-20240322163226170](https://typora-kpl.oss-cn-hangzhou.aliyuncs.com/image-20240322163226170.png)


## 3.向keywords表中插入监听对象(默认对象都为 群组)
1. 运行utils/keywords.py文件里的check_keywords_from_db()函数，向keywords表中插入Bot识别的关键词，根据提示进行操作即可

![image-20240322163250618](https://typora-kpl.oss-cn-hangzhou.aliyuncs.com/image-20240322163250618.png)

## 4.运行Bot主程序
1. 进入wxchatbot.py，找到文件末尾，打开Bot.Listen_Sensitive()的注释
![img.png](https://typora-kpl.oss-cn-hangzhou.aliyuncs.com/img.png)
2. 使用命令 `python wxchatbot.py` 启动Bot主程序
3. 如果提前已经向表listen_list和keywords中插入监听对象和关键词，则Bot开始运行，否则命令行会出现要求输入信息的提示
4. Bot启动时，程序会模拟人手动操作微信的动作，鼠标会被接管，Bot会自动打开listen_list中监听对象的对话窗口(独立出来一个窗口)，随后Bot会在n个监听对象之间的窗口来回切换，每隔一段时间查询一次所有监听对象的消息
5. 当Bot识别到监听对象发送的消息中的关键字时，自动发送keywords中对应的回复消息，如果是文本就发消息，如果是图片和文件，就发送图片和文件给用户，图片会被自动保存到程序主目录下的 微信图片 文件夹里
![img_1.png](https://typora-kpl.oss-cn-hangzhou.aliyuncs.com/img_1.png).