# -*- coding: utf-8 -*-
# @Time : 2022/9/4
# @FileName: main.py
# @Software: PyCharm

import const  # 自定义常量库
import utils  # 自定义工具库
import daka  # 打卡模块
# import private_info #
import os

# 账号 密码等信息 Actions部署
id = os.environ["id"]
pwd = os.environ["pwd"]
# 邮箱信息
MAIL_USER = os.environ["MAIL_USER"]  # QQ邮箱账户
MAIL_PWD = os.environ["MAIL_PWD"]  # QQ邮箱授权码
MAIL_TO = os.environ["MAIL_TO"]  # QQ邮箱账户

# 本地运行就直接填上相应信息，所有信息需要被双引号""包裹
# id = "学号"
# pwd = "健康上报密码"
# MAIL_USER = "发送信息邮箱"
# # 这里是授权码--不是账户密码
# MAIL_PWD = "发送信息邮箱授权码"
# MAIL_TO = "接收信息邮箱"


# 本地自己设置private_info.py

# id = private_info.id
# pwd = private_info.pwd
# MAIL_TO = private_info.MAIL_TO
# # 多用户下name进行一对一提示--列表对象
# name = private_info.name
# # 以下为常量
# MAIL_USER = private_info.MAIL_USER
# # 这里是授权码--不是账户密码
# MAIL_PWD = private_info.MAIL_PWD


# 账号和密码需要被双引号""包裹
#   eg:
#       id = "学号"
#       pwd = "密码"


if __name__ == '__main__':
    # 打卡
    msg = daka.sign_in(id=id, pwd=pwd, name=str(id), check_today=0)
    # 发送邮件
    utils.mail(msg, MAIL_TO, MAIL_USER=MAIL_USER, MAIL_PWD=MAIL_PWD)
