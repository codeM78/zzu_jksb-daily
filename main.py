# -*- coding: utf-8 -*-
# @Time : 2022/9/4
# @FileName: main.py
# @Software: PyCharm


import utils  # 自定义工具库
import daka  # 打卡模块
import os

# 账号 密码等信息 Actions部署
id = os.environ["id"]
pwd = os.environ["pwd"]
# 邮箱信息
MAIL_USER = os.environ["MAIL_USER"]  # QQ邮箱账户
MAIL_PWD = os.environ["MAIL_PWD"]  # QQ邮箱授权码
MAIL_TO = os.environ["MAIL_TO"]  # QQ邮箱账户



if __name__ == '__main__':
    # 打卡
    msg = daka.sign_in(id=id, pwd=pwd, name=str(id), check_today=0)
    # 发送邮件
    utils.mail(msg, MAIL_TO, MAIL_USER=MAIL_USER, MAIL_PWD=MAIL_PWD)
