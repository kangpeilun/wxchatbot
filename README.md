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
git clone --recursive https://github.com/kangpeilun/wxchatbot.git
cd wxchatbot
pip install -r requirements.txt
```

下载并安装64位orcale数据库，下载连接：https://www.cnblogs.com/liuhongfeng/p/5267549.html

# 使用方法

> 1. bot_param.py 文件中存放着控制Bot的相关参数，注释写的很详细，除了注明debug使用的外，其他的不要随便修改
>
> ![image-20240322163108425](https://typora-kpl.oss-cn-hangzhou.aliyuncs.com/image-20240322163108425.png)
>
> 2. 切记：登录在电脑上的微信作为Bot，跟微信是谁的没有关系，比如我的账号登录了微信，那么我的账号就变成了一个自动发消息的Bot，只是我的昵称没有改成Bot罢了
## 1.创建listen_list, keywords, bot_chat_info, bot_service, service_user_chat, all_msg六张表
```python
# listen_list表字段, 可以根据需求自己修改变量类型
id number # pk
listen_name varchar2(150)

# keywords表字段, 可以根据需求自己修改变量类型
id number  # pk
keyword varchar2(150)
reply clob
reply_type varchar2(10) = 'text'  # 默认值为'text'

# bot_chat_info表字段, 注意由原来的chat_info变为bot_chat_info
id number  # pk
user_name varchar2(150)
user_group varchar2(150)
user_text clob
reply clob
reply_type varchar2(10) = NULL  # 默认值为NULL
time date=SYSDATE  # 自动填充系统时间

# bot_service表字段
id number  # pk
bot_name varchar2(15)  # Bot名称
service_name varchar2(15)  # Bot对应的客服名称

# service_user_chat表字段，人工客服与客户的对话记录
id number  # pk
user_name varchar2(20)
user_group varchar2(20)
user_question clob
service_name varchar2(20)
service_reply clob=NULL  # 因为客服的回复难以实时与客户的问题一一对应存储起来，故该字段先默认为NULL
time date=SYSDATE

# all_msg表字段，存储群聊里的所有消息
id number  # pk
user_name varchar2(20)
user_group varchar2(20)
user_text clob
time date=SYSDATE


# 同时设置了6个sequences，用于三张表的主键自增
listen_list_seq
keywords_seq
bot_chat_info_seq
bot_service_seq
service_user_chat_seq
all_msg_seq
```

`在utils/database.py中配置数据库连接信息`
![image-20240328141835231](https://typora-kpl.oss-cn-hangzhou.aliyuncs.com/image-20240328141835231.png)

![image-20240328141143642](https://typora-kpl.oss-cn-hangzhou.aliyuncs.com/image-20240328141143642.png)

![image-20240322162946623](https://typora-kpl.oss-cn-hangzhou.aliyuncs.com/image-20240322162946623.png)

![image-20240322163003764](https://typora-kpl.oss-cn-hangzhou.aliyuncs.com/image-20240322163003764.png)

## 2.向listen_list表中插入监听对象(默认对象都为 群组)

1. 运行utils/listen_list.py文件里的check_listen_list_from_db()函数，向listen_list表中插入监听对象，根据提示进行操作即可

![image-20240322163226170](https://typora-kpl.oss-cn-hangzhou.aliyuncs.com/image-20240322163226170.png)


## 3.向keywords表中插入监听对象(默认对象都为 群组)
1. 运行utils/keywords.py文件里的check_keywords_from_db()函数，向keywords表中插入Bot识别的关键词，根据提示进行操作即可

![image-20240322163250618](https://typora-kpl.oss-cn-hangzhou.aliyuncs.com/image-20240322163250618.png)

## 4.向bot_service表中插入Bot对应的客服名称

1. 运行utils/bot_service.py文件中的check_bot_service_from_db()函数，插入Bot对应的客服名称，根据提示输入即可

`注意：`**客服的名称为Bot这个微信号上所添加的客服的账号你备注的昵称**

> 比如Bot1对应的人工客服为 电力小哥，即使电力小哥的微信原名为xxx，在添加bot_service表时，客服名仍要填入 电力小哥

![image-20240328134845346](https://typora-kpl.oss-cn-hangzhou.aliyuncs.com/image-20240328134845346.png)

![image-20240328141010873](https://typora-kpl.oss-cn-hangzhou.aliyuncs.com/image-20240328141010873.png)

## 运行Bot主程序

1. 进入wxchatbot.py，找到文件末尾，打开**Bot.Run_Bot()**的注释
    ![image-20240328140354167](https://typora-kpl.oss-cn-hangzhou.aliyuncs.com/image-20240328140354167.png)
2. 使用命令 `python wxchatbot.py` 启动Bot主程序
3. Bot首先会检查数据库中是否缺少必要的数据，如果确实，则会提示进行输入，请按照要求输入即可
4. 如果数据库未缺少必要数据，则Bot正式启动
5. Bot启动时，程序会模拟人手动操作微信的动作，鼠标会被接管，Bot会自动打开listen_list中监听对象的对话窗口(独立出来一个窗口)，随后Bot会在n个监听对象之间的窗口来回切换，每隔一段时间查询一次所有监听对象的消息
6. 当Bot识别到监听对象发送的消息中的关键字时，自动发送keywords中对应的回复消息，如果是文本就发消息，如果是图片和文件，就发送图片和文件给用户，图片会被自动保存到程序主目录下的 微信图片 文件夹里，同时将运行过程中的一切消息存入数据库中。如果是图片消息，图片会被存入本地的 "微信图片" 文件夹，同时将文件绝对路径存入all_msg中的user_text字段中
    ![image-20240328140918720](https://typora-kpl.oss-cn-hangzhou.aliyuncs.com/image-20240328140918720.png).