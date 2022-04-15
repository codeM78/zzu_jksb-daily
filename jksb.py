# -*- coding: utf-8 -*-
# @Time : 2022/4/9 10:15


import re
import requests
import json  # 用于读取账号信息
import time  # 用于计时重新发送requests请求
import base64  # 用于解密编码
import logging  # 用于日志控制
import os, sys
from lxml import etree  # 可以利用Xpath进行文本解析的库
# 发送邮件的库
import smtplib
from email.mime.text import MIMEText

# 账号 密码等信息 Actions部署
id = os.environ["id"]
pwd = os.environ["pwd"]
# 邮箱信息
MAIL_USER = os.environ["MAIL_USER"]  # QQ邮箱账户
MAIL_PWD = os.environ["MAIL_PWD"]  # QQ邮箱授权码
MAIL_TO = os.environ["MAIL_TO"]  # QQ邮箱账户


# 本地运行就直接填上相应信息，所有信息需要被双引号""包裹
# id = "学号"
# pwd = "密码"
# MAIL_USER = "QQ邮箱账户"
# # 这里是授权码--不是账户密码
# MAIL_PWD = "邮箱授权码"
# MAIL_TO = "QQ邮箱账户"

# 账号和密码需要被双引号""包裹
#   eg:
#       id = "学号"
#       pwd = "密码"

def sign_in(id, pwd):
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    r = ""

    # set logging format
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
    # create a log file at the work directory

    # 日志文件my.log会保存在该python文件所在目录当中
    logging.basicConfig(filename=curr_dir + '/my.log', level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)

    logging.info("===开始打卡===")

    # login
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36 Edg/100.0.1185.29',
        'referer': 'https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/first0?fun2=a',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    form = {
        "uid": id,
        "upw": pwd,
        "smbtn": "进入健康状况上报平台",
        "hh28": "750"  # 按照当前浏览器窗口大小计算
    }
    r = ""
    max_punch = 10
    curr_punch = 0  # if curr_punch > max_pubch then exit
    logging.info("准备进入打卡界面")
    while True:
        try:
            logging.info("准备进入post请求")
            r = requests.post("https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/login", headers=headers, data=form,
                              timeout=(200, 200))  # response为账号密码对应的ptopid和sid信息,timeout=60(sec)
            logging.info("成功运行post请求")
        except:
            logging.warning("请检查网络链接是否正常")
            curr_punch += 1
            if curr_punch > max_punch:
                exit()
            time.sleep(120)  # sleep 60 sec
        else:
            break
    text = r.text.encode(r.encoding).decode(r.apparent_encoding)  # 解决乱码问题
    r.close()
    del (r)
    # first6
    # 获取sid和ptopid
    matchObj = re.search(r'ptopid=(\w+)\&sid=(\w+)\"', text)

    try:
        ptopid = matchObj.group(1)
        sid = matchObj.group(2)

    except:
        logging.warning("请检查账号" + id + "和密码" + pwd + "是否正确，或检查是否有验证码")
        exit()
    else:
        logging.info("账号密码正确")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36 Edg/100.0.1185.29',
        'referer': 'https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/login'
    }
    curr_punch = 0
    while True:
        try:
            r = requests.get(
                "https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb?ptopid=" + ptopid + "&sid=" + sid + "&fun2=")  # response里含有jksb对应的params
        except:
            logging.error("get请求失败")
            if curr_punch > max_punch:
                exit()
            curr_punch += 1
            time.sleep(120)
        else:
            break
    text = r.text.encode(r.encoding).decode(r.apparent_encoding)  # 解决乱码问题


    # 获取fun18参数
    matchObj_fun18 = re.findall(r'name="fun18" value="(\d+)"', text)
    fun18 = matchObj_fun18[0]


    tree = etree.HTML(text)
    nodes = tree.xpath('//*[@id="bak_0"]/div[5]/span')
    # 如果今日填报过就退出填报，直接返回msg
    if nodes[0].text == "今日您已经填报过了":
        return nodes[0].text
    r.close()
    del (r)

    # jksb?with_params
    matchObj = re.search(r'ptopid=(\w+)\&sid=(\w+)\&', text)
    ptopid = matchObj.group(1)
    sid = matchObj.group(2)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36 Edg/100.0.1185.29',
        'referer': 'https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/login'
    }
    curr_punch = 0
    while True:
        try:
            r = requests.get(
                "https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb?ptopid=" + ptopid + "&sid=" + sid + "&fun2=",
                headers=headers)  # response为jksb表单第一页
        except:
            logging.info("第二次get请求失败")
            while curr_punch > max_punch:
                exit()
            curr_punch += 1
            time.sleep(120)
        else:
            break
    ptopid1 = ptopid
    sid1 = sid

    text = r.text.encode(r.encoding).decode(r.apparent_encoding)  # 解决乱码问题
    r.close()
    del (r)

    # DONE 最后提交表单
    matchObj = re.search(r'name=\"ptopid\" value=\"(\w+)\".+name=\"sid\" value=\"(\w+)\".+', text)
    ptopid = matchObj.group(1)
    sid = matchObj.group(2)

    fun18 = fun18
    form = {
        "day6": "b",
        "did": "1",
        "door": "",
        "fun18":fun18,
        "men6": "a",
        "ptopid": ptopid,
        "sid": sid
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36 Edg/100.0.1185.29',
        'Referer': 'https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb?ptopid=' + ptopid1 + '&sid=' + sid1 + '&fun2=',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'jksb.v.zzu.edu.cn',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Microsoft Edge";v="100"',
        'Origin': 'https://jksb.v.zzu.edu.cn',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Sec-Fetch-Dest': 'iframe',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',

    }
    while True:
        try:
            r = requests.post("https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb", headers=headers,
                              data=form)  # response为打卡的第二个表单
        except:
            while curr_punch > max_punch:
                exit()
            curr_punch += 1
        else:
            break
    text = r.text.encode(r.encoding).decode(r.apparent_encoding)  # 解决乱码问题


    r.close()
    del (r)


    # DONE  最后提交表单，跳转完成页面
    matchObj = re.search(r'name=\"ptopid\" value=\"(\w+)\".+name=\"sid\" value=\"(\w+)\"', text)
    ptopid = matchObj.group(1)
    sid = matchObj.group(2)
    form = {
        "myvs_1": "否",
        "myvs_2": "否",
        "myvs_3": "否",
        "myvs_4": "否",
        "myvs_5": "否",
        "myvs_6": "否",
        "myvs_7": "否",
        "myvs_8": "否",
        "myvs_9": "否",
        "myvs_10": "否",
        "myvs_11": "否",
        "myvs_12": "否",
        # "myvs_13": "g",  # 这是green绿码，但是已经对接郑好办，弃用
        "myvs_13a": "41",
        "myvs_13b": "4101",
        "myvs_13c": "河南省.郑州市",
        "myvs_24": "否",
        "myvs_26": "5",  # 两针疫苗，5是三针
        "myvs_14b": "",  # 该选项已弃用
        "memo22": "[待定]",
        "did": "2",
        "door": "",
        "day6": "b",
        "men6": "a",
        "sheng6": "",
        "shi6": "",
        "fun3": "",
        "jingdu": "113.658333", # 北校区经度,jingdu=113.658055
        "weidu": "34.782222",   # 北校区纬度,&weidu=34.782807  东经113.658333北纬34.7822222
        "ptopid": ptopid,
        "sid": sid,
        "fun18": fun18,
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36 Edg/100.0.1185.29',
        'Referer': 'https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'jksb.v.zzu.edu.cn',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Microsoft Edge";v="100"',
        'Origin': 'https://jksb.v.zzu.edu.cn',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Sec-Fetch-Dest': 'iframe',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',



    }
    while True:
        try:
            r = requests.post("https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb", data=form,
                              headers=headers)  # response为完成打卡页面
        except:
            while curr_punch > max_punch:
                exit()
            curr_punch += 1
        else:
            break
    text = r.text.encode(r.encoding).decode(r.apparent_encoding)  # 解决乱码问题


    r.close()
    del (r)
    # 匹配成功页面
    matchObj_succeed = re.findall(r"感谢[你您]今日上报健康状况！", text)
    msg = matchObj_succeed[0]
    print(msg)

    # # 非正常页面 //*[@id="bak_0"]/div[2]/div[2]/div[2]/div[2]/li
    # nodes_li = tree.xpath('//*[@id="bak_0"]/div[2]/div[2]/div[2]/div[2]/li')
    # global msg_li
    # for _ in nodes_li:
    #     msg_li = _.text
    #     # print(msg_li)

    if ("今日上报健康状况！" in msg):
        logging.info(id + ":打卡成功\n")
        print(id + ":打卡成功")

    else:
        logging.info(id + ":打卡失败\n")
        print(id + ":打卡失败")

    if msg != None:
        return msg
    else:
        return 'Null，今日打卡失败！'



# 发送邮件的函数
def mail(mail_text, mail_to):
    # set the mail context
    msg = MIMEText(mail_text)

    # set the mail info
    msg['Subject'] = "每日健康打卡通知"  # 主题
    msg['From'] = MAIL_USER
    msg['To'] = mail_to

    # send the mail
    # 发送到QQ邮箱
    send = smtplib.SMTP_SSL("smtp.qq.com", 465)
    send.login(MAIL_USER, MAIL_PWD)
    send.send_message(msg)
    # quit QQ EMail
    send.quit()


if __name__ == '__main__':
    msg = sign_in(id=id, pwd=pwd)
    # print(msg)
    mail(msg, MAIL_TO)
