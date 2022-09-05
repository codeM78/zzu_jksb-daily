# -*- coding: utf-8 -*-
# @Time : 2022/9/4
# @FileName: daka.py
# @Software: PyCharm
import random
import re
import requests
import json  # 用于读取账号信息
import time  # 用于计时重新发送requests请求
import base64  # 用于解密编码
import logging  # 用于日志控制
import os, sys

from lxml import etree  # 可以利用Xpath进行文本解析的库

import utils # 导入工具包
import const # 导入常量包

# 用于打卡的脚本
def sign_in(id, pwd, name="Turing", check_today=1):
    '''

    :param id: 学号
    :param pwd: 密码
    :param name: 姓名提示，默认为Turing
    :param check_today: 检查今日是否已经填报，默认为1（True）
    :return: 打卡成功与否的msg
    '''
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    r = ""

    # set logging format
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
    HANDLERS = ""

    # create a log file at the work directory

    # 日志文件my.log会保存在该python文件所在目录当中
    logging.basicConfig(filename=curr_dir + '/daka.log',
                        level=logging.INFO, format=LOG_FORMAT,
                        datefmt=DATE_FORMAT)

    logging.info("===开始打卡===")

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
            # post请求记得关闭证书错误忽略 verify=False
            r = requests.post("https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/login", headers=headers, data=form,
                              timeout=(200, 200), verify=False)  # response为账号密码对应的ptopid和sid信息,timeout=60(sec)
            logging.info("成功运行post请求")
        except Exception as e:
            logging.warning("请检查网络链接是否正常")
            logging.warning(e)
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
        logging.warning("请检查账号" + id + "和密码" + pwd + "是否正确，或检查是否有验证码")
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
            r = requests.get(
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

    # jksb?with_params  获取参数ptoid和sid
    matchObj = re.search(r'ptopid=(\w+)\&sid=(\w+)\&', text)
    ptopid = matchObj.group(1)
    sid = matchObj.group(2)

    headers = {
        'User-Agent': const.Const.USER_AGENT.value,
        'referer': 'https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/login'
    }
    curr_punch = 0
    while True:
        try:
            r = requests.get(
                "https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb?ptopid=" + ptopid + "&sid=" + sid + "&fun2=",
                headers=headers, verify=False)  # response为jksb表单第一页
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
    # DONE 填写表单页面
    matchObj = re.search(r'name=\"ptopid\" value=\"(\w+)\".+name=\"sid\" value=\"(\w+)\".+', text)
    ptopid = matchObj.group(1)
    sid = matchObj.group(2)

    fun18 = fun18
    form = {
        "day6": "b",
        "did": "1",
        "door": "",
        "fun18": fun18,
        "men6": "a",
        "ptopid": ptopid,
        "sid": sid
    }
    headers = {
        'User-Agent': const.Const.USER_AGENT.value,
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
                              data=form, verify=False)  # response为打卡的第二个表单
        except:
            while curr_punch > max_punch:
                exit()
            curr_punch += 1
        else:
            break
    text = r.text.encode(r.encoding).decode(r.apparent_encoding)  # 解决乱码问题
    # print(text)  # 表单填写页
    r.close()
    del (r)

    # 接下来获取 text中的图片值，并本地化保存
    imgurl = utils.get_img_urls(html=text, index=0)
    # 获取当前文件当前绝对路径
    path = os.getcwd()
    # 图片存储路径
    dest = path + r"/vcode.png"
    utils.imgurl2pic(imgurl=imgurl, dest=dest)

    # 将图片验证码转换为文本
    vcode_text = utils.pic2vcode_2(dest)
    # 如果是大写中文数字再转换为阿拉伯数字
    vcode = utils.chineseNumber2Num(vcode_text)

    # DONE  最后提交表单，跳转完成页面
    matchObj = re.search(r'name=\"ptopid\" value=\"(\w+)\".+name=\"sid\" value=\"(\w+)\"', text)
    ptopid = matchObj.group(1)
    sid = matchObj.group(2)
    form = {
        # 验证码识别
        "myvs_94c": vcode,
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
        # "jingdu": "113.658333",  # 经度
        # "weidu": "34.782222",  # 纬度
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
            r = requests.post("https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb", data=form,
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
            r = requests.get(
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

