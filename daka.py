# -*- coding: utf-8 -*-
# @Time : 2022/11/27
# @FileName: daka.py
# @Software: PyCharm
import re
import random

import requests
# 用来降低服务器方ssl版本
from requests_toolbelt import SSLAdapter

import time  # 用于计时重新发送requests请求
import logging  # 用于日志控制
import os

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

    # # 获取登录页面验证码
    # imgurl = const.Const.LOGIN_VCODE_URL.value
    # # 获取当前文件当前绝对路径
    # path = os.getcwd()
    # # 图片存储路径
    # dest = path + r"/num_vcode.png"
    # utils.imgurl2pic(imgurl=imgurl, dest=dest)
    #
    # # 将图片验证码转换为文本列表
    # # num_vcode = utils.baidu_OCR(dest, use_accurate=True)
    # num_vcode = utils.pic2vcode(dest)
    # logging.info(f"此次获取的图片值为：{num_vcode}")
    # if num_vcode == "":
    #     logging.info(name + ": " + id + ":验证码为空，打卡失败\n")

    # 设置验证码为空
    num_vcode = ""
    # login
    headers = {
        'User-Agent': const.Const.USER_AGENT.value,
        'referer': 'https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/first0?fun2=a',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    form = {
        "uid": id,
        "upw": pwd,
        # 登录页面验证码
        "ver6": num_vcode,
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
            # post请求记得关闭证书错误忽略 verify=False
            # 这里所有的原来都是requests.(post|get)
            r = s.post("https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/login", headers=headers, data=form,
                       timeout=(200, 200), verify=False)  # response为账号密码对应的ptopid和sid信息,timeout=60(sec)
            logging.info("成功运行post请求")
        except Exception as e:
            logging.error("请检查网络链接是否正常")
            logging.error(str(e) + "\n")
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

    except Exception as e:
        logging.error("请检查账号" + id + "和密码" + pwd + "是否正确，或检查是否有验证码\n")
        logging.error("ptopid和sid获取失败：" + str(e))
        return "今日打卡失败！请手动打卡。（error：请检查账号和密码是否正确，或是否有验证码）。"
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
            logging.error("get请求失败\n")
            if curr_punch > max_punch:
                exit()
            curr_punch += 1
            time.sleep(120)
        else:
            break
    text = r.text.encode(r.encoding).decode(r.apparent_encoding)  # 解决乱码问题
    # print(text) # 本人填报按钮页

    # 获取fun218参数
    try:
        matchObj_fun218 = re.findall(r'name="fun218" value="(\d+)"', text)
        fun218 = matchObj_fun218[0]
    except Exception as e:
        logging.error("找不到fun218 " + str(e))
        fun218 = ""

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
            r = s.get(
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

    fun218 = fun218
    form = {
        "day6": "b",
        "did": "1",
        "door": "",
        "fun218": fun218,
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
            r = s.post("https://jksb.v.zzu.edu.cn/vls6sss/zzujksb.dll/jksb", headers=headers,
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

    # # 接下来获取 text中的图片值，并本地化保存
    imgurl = utils.get_img_urls(html=text, index=0)
    # 如果有验证码url
    if imgurl != "找不到img标签":
        # 获取当前文件当前绝对路径
        path = os.getcwd()
        # 图片存储路径
        dest = path + r"/vcode.png"
        utils.imgurl2pic(imgurl=imgurl, dest=dest)

        # 将图片验证码转换为文本列表
        vcode_text = utils.baidu_OCR(dest, use_hand=True)
        if vcode_text == "":
            logging.info(name + ": " + id + ":验证码为空，打卡失败\n")
            return "很遗憾！今日打卡失败！请先自行打卡"
        # 如果是大写中文数字再转换为阿拉伯数字
        vcode = utils.chineseNumber2Num(vcode_text)
        logging.info(f"此次获取的图片值为：{vcode_text}--->{vcode}")
    # 如果没有验证码
    else:
        vcode = ""

    # DONE  最后提交表单，跳转完成页面
    matchObj = re.search(r'name=\"ptopid\" value=\"(\w+)\".+name=\"sid\" value=\"(\w+)\"', text)
    ptopid = matchObj.group(1)
    sid = matchObj.group(2)

    form = {
        # 多了个验证码识别,需要将img图片下载下来，然后使用图片识别工具，识别出数字并赋值
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
        "fun218": fun218,  # 从fun18变成了fun218 动态变化，用来检测脚本
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
            logging.error("get请求失败\n")
            if curr_punch > max_punch:
                exit()
            curr_punch += 1
            time.sleep(120)
        else:
            break
    text = r.text.encode(r.encoding).decode(r.apparent_encoding)  # 解决乱码问题
    # print(text)

    # # 获取fun218参数
    # matchObj_fun218 = re.findall(r'name="fun218" value="(\d+)"', text)
    # fun218 = matchObj_fun218[0]
    # # print(f"1:{fun218}")

    tree = etree.HTML(text)
    nodes = tree.xpath('//*[@id="bak_0"]/div[5]/span')
    # 如果今日填报过就退出填报，直接返回msg
    if nodes[0].text == "今日您已经填报过了":
        logging.info(name + ": " + id + ":打卡成功\n")
        return name + ": 恭喜您，" + nodes[0].text
    else:
        logging.info(name + ": " + id + ":打卡失败\n")
        return "很遗憾！今日打卡失败！请先自行打卡"

    r.close()
    del (r)

