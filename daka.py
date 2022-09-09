# -*- coding: utf-8 -*-
# @Time : 2022/9/7
# @FileName: daka.py
# @Software: PyCharm
import random
import re
import requests
# 用来降低服务器方ssl版本
from requests_toolbelt import SSLAdapter

import time  # 用于计时重新发送requests请求
import base64  # 用于解密编码
import logging  # 用于日志控制
import os, sys

import urllib3
from lxml import etree  # 可以利用Xpath进行文本解析的库

import const
import utils



# 用于打卡的脚本
def sign_in(id, pwd, name="Turing", check_today=1):
    '''

    :param id: 学号
    :param pwd: 密码
    :param name: 姓名提示，默认为Turing
    :param check_today: 检查今日是否已经填报，默认为1（True）
    :return: 打卡成功与否的msg
    '''
    # INFO级别的日志文件
    utils.my_log("daka.log")

    logging.info("===开始打卡===")
    # 去除 ssl警告
    urllib3.disable_warnings()

    # login
    headers = {
        'User-Agent': const.Const.USER_AGENT.value,
        'referer': 'https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/first0?fun2=a',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    form = {
        "uid": id,
        "upw": pwd,
        "smbtn": "进入健康状况上报平台",
        "hh28": "969"  # 按照当前浏览器窗口大小计算
    }
    r = ""
    max_punch = 10
    curr_punch = 0  # if curr_punch > max_pubch then exit
    logging.info("准备进入打卡界面")
    while True:
        try:
            logging.info("准备进入post请求")
            s = requests.session()
            s.keep_alive = False  # 关闭多余连接
            # 降低版本适配ssl
            adapter = SSLAdapter('TLSv1')
            s.mount('https://', adapter)
            # post请求记得关闭证书错误忽略 verify=False 这里原来是 requests.post
            r = s.post("https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/login", headers=headers, data=form,
                              timeout=(200, 200), verify=False)  # response为账号密码对应的ptopid和sid信息,timeout=60(sec)
            logging.info("成功运行post请求")
        except Exception as e:
            logging.error("请检查网络链接是否正常")
            logging.error(e)
            curr_punch += 1
            if curr_punch > max_punch:
                exit()
            time.sleep(60)  # sleep 60 sec
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
        logging.error("请检查账号" + id + "和密码" + pwd + "是否正确，或检查是否有验证码")
        return "今日打卡失败！请手动打卡。（error：检查是否有验证码）。"
        exit()
    else:
        logging.info("账号密码正确")
    headers = {
        'User-Agent': const.Const.USER_AGENT.value,
        'referer': 'https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/login'
    }
    curr_punch = 0
    while True:
        try:
            r = s.get(
                "https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb?ptopid=" + ptopid + "&sid=" + sid + "&fun2=",
                headers=headers, verify=False)  # response里含有jksb对应的params
        except:
            logging.error("get请求失败")
            if curr_punch > max_punch:
                exit()
            curr_punch += 1
            time.sleep(120)
        else:
            break
    text = r.text.encode(r.encoding).decode(r.apparent_encoding)  # 解决乱码问题
    # print(text) # 本人填报按钮页

    # 获取fun18参数
    matchObj_fun18 = re.findall(r'name="fun18" value="(\d+)"', text)
    fun18 = matchObj_fun18[0]
    # print(f"1:{fun18}")

    tree = etree.HTML(text)
    nodes = tree.xpath('//*[@id="bak_0"]/div[5]/span')
    # 如果今日填报过就退出填报，直接返回msg
    if check_today:
        if nodes[0].text == "今日您已经填报过了":
            logging.info(name + ": " + id + ":打卡成功\n")
            return name + ": 恭喜您，" + nodes[0].text

    r.close()
    del (r)


    # DONE  最后提交表单，跳转完成页面
    ptopid = ptopid
    sid = sid
    form = {
        # 多了个验证码识别,需要将img图片下载下来，然后使用图片识别工具，识别出数字并赋值
        # "myvs_94c": vcode,
        "myvs_1": "否",
        "myvs_2": "否",
        "myvs_3": "否",
        "myvs_4": "否",
        "myvs_5": "否",
        # "myvs_6": "否",
        "myvs_7": "否",
        "myvs_8": "否",
        # "myvs_9": "y", # 已经接入郑好办，现在弃用  昨日核酸：n是没有做；x是没要求做，y是做了
        # "myvs_10": "否",
        "myvs_11": "否",
        "myvs_12": "否",
        "myvs_13": "否",
        "myvs_15": "否",

        "myvs_13a": "41",  # 省份（自治区）：省份编码  对应身份证前两位  河南省=41
        "myvs_13b": "4101",  # 地市：地级市编码 对应身份证前四位  郑州市=4101
        "myvs_13c": "河南省.郑州市",  # 自己填写当前所在地即可
        "myvs_24": "否",
        "myvs_26": "5",  # 疫苗接种情况：0是待选；1是1针剂；2是2针剂；3是尚未接种；4是有禁忌症，无法接种；5是三针3针剂
        # "myvs_14b": "",  # 该选项已弃用
        "memo22": "请求超时",  # [待定] 位置获取情况
        "did": "2",  # 以此为界 往下为hidden值
        "door": "",
        "day6": "",  # 原值=6
        "men6": "a",
        "sheng6": "",
        "shi6": "",
        "fun18": fun18,  # fun18 动态变化，用来检测脚本
        "fun3": "",
        # "jingdu": "113.658333",  # 经度： 北校区经度,jingdu=113.658055
        # "weidu": "34.782222",  # 纬度： 北校区纬度,&weidu=34.782807  东经113.658333北纬34.7822222
        "ptopid": ptopid,
        "sid": sid,
    }
    headers = {
        'User-Agent': const.Const.USER_AGENT.value,
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
            r = s.post("https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb", data=form,
                              headers=headers, verify=False)  # response为完成打卡页面
        except:
            while curr_punch > max_punch:
                exit()
            curr_punch += 1
        else:
            break
    text = r.text.encode(r.encoding).decode(r.apparent_encoding)  # 解决乱码问题
    # 打印出最后成功的页面  处理一下【你今日的健康状态上报信息已通过审核，今日不能再修改】这个问题  其实也不用解决，因为会返回今日您已经填报过了！
    # print(text)

    r.close()
    del (r)

    headers = {
        'User-Agent': const.Const.USER_AGENT.value,
        'referer': 'https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/login'
    }
    curr_punch = 0
    while True:
        try:
            r = s.get(
                "https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb?ptopid=" + ptopid + "&sid=" + sid + "&fun2=",
                headers=headers, verify=False)  # response里含有jksb对应的params
        except:
            logging.error("get请求失败")
            if curr_punch > max_punch:
                exit()
            curr_punch += 1
            time.sleep(120)
        else:
            break
    text = r.text.encode(r.encoding).decode(r.apparent_encoding)  # 解决乱码问题
    # print(text)

    # # 获取fun18参数
    # matchObj_fun18 = re.findall(r'name="fun18" value="(\d+)"', text)
    # fun18 = matchObj_fun18[0]
    # # print(f"1:{fun18}")

    tree = etree.HTML(text)
    nodes = tree.xpath('//*[@id="bak_0"]/div[5]/span')
    # 如果今日填报过就退出填报，直接返回msg
    if nodes[0].text == "今日您已经填报过了":
        logging.info(name + ": " + id + ":打卡成功\n")
        return name + ": 恭喜您，" + nodes[0].text
    else:
        logging.info(name + ": " + id + ":打卡失败\n")
        return name + ": 很遗憾，今日打卡失败！请先自行打卡"

    r.close()
    del (r)


