# -*- coding: utf-8 -*-
# @Time : 2022/9/6
# @FileName: utils.py
# @Software: PyCharm
import logging
import os
import re
# 邮件发送模块
import smtplib
from email.mime.text import MIMEText
# import private_info
# 验证码模块
# import ddddocr

# # 大写数字验证码模块
# from cnocr.utils import read_img
# from cnocr import CnOcr
# 网页请求模块
import requests
# 用来降低服务器方ssl版本
from requests_toolbelt import SSLAdapter


def my_log(filename: str):
    curr_dir = os.path.dirname(os.path.abspath(__file__))

    # set logging format
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"

    # 在logging.basicConfig前清理已有 handlers  防止其他包提前使用日志系统，导致level不起作用
    root_logger = logging.getLogger()
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)

    # 日志文件保存在该python文件所在目录当中
    logging.basicConfig(filename=curr_dir + '/' + filename,
                        level=logging.INFO, format=LOG_FORMAT,
                        datefmt=DATE_FORMAT)


# 获取所有的img 默认返回img url列表
def get_img_urls(html, index=None):
    '''

    :param html: 获取的网页文本
    :param index: 需要的url索引
    :return:
    '''
    replace_pattern = r'<img.*?/>'  # img标签的正则式
    img_url_pattern = r'.+?src="(\S+)"'  # img_url的正则式
    img_url_list = []
    need_replace_list = re.findall(replace_pattern, html)  # 找到所有的img标签
    if need_replace_list == [] or need_replace_list == None:
        return need_replace_list

    for tag in need_replace_list:
        img_url_list.append(re.findall(img_url_pattern, tag)[0])  # 找到所有的img_url

    return img_url_list if index == None else img_url_list[index]


def imgurl2pic(imgurl, dest: str):
    s = requests.session()
    s.keep_alive = False  # 关闭多余连接
    # 降低版本适配ssl
    adapter = SSLAdapter('TLSv1')
    s.mount('https://', adapter)
    res = s.get(imgurl)

    with open(dest, 'wb') as f:
        f.write(res.content)
    logging.info("图片获取成功！")
    return "图片获取成功！"


# # 将数字图片验证码转换为文本
# def pic2vcode(pic_path: str):
#     '''
#
#     :param pic_path: 本地图片验证码路径
#     :return: 文本验证码
#     '''
#     ocr = ddddocr.DdddOcr()
#     with open(pic_path, 'rb') as f:
#         img_bytes = f.read()
#     vcode = ocr.classification(img_bytes)
#     return vcode


# # CnOcr() 实现验证码识别
# def pic2vcode_2(pic_path: str):
#     ocr = CnOcr()
#     img = read_img(pic_path)
#     res = ocr.ocr(img)
#     return res[0].get("text")


# 将大写的数字转换为阿拉伯数字
def chineseNumber2Num(strNum: str) -> str:
    # 去掉strNum多余空格
    strNum = strNum.replace(" ", "")

    res = ""
    # 零壹贰叁肆伍陆柒捌玖
    cnArr = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
    for i in range(len(strNum)):
        c = strNum[i]
        for j in range(len(cnArr)):
            if c == cnArr[j]:
                res = res + str(j)
    # 去掉res多余空格
    res = res.replace(" ", "")
    return res if res != "" else strNum


# 发送邮件的函数
def mail(mail_text, mail_to, MAIL_USER, MAIL_PWD):
    '''

    :param mail_text: 发送的文本
    :param mail_to: 发送给~
    :param MAIL_USER: 发送的邮箱
    :param MAIL_PWD: 发送邮箱的授权码
    :return:
    '''
    # set the mail context
    msg = MIMEText(mail_text)

    # set the mail info
    msg['Subject'] = mail_text  # 主题
    msg['From'] = MAIL_USER
    msg['To'] = mail_to

    # send the mail
    # 发送到QQ邮箱
    send = smtplib.SMTP_SSL("smtp.qq.com", 465)
    send.login(MAIL_USER, MAIL_PWD)
    send.send_message(msg)
    # quit QQ EMail
    send.quit()



