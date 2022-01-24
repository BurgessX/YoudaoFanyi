"""
有道翻译爬虫
2021/11/13 根据视频教程 https://www.bilibili.com/video/BV1wp4y1z7L6?p=4 测试成功
2022/01/24 对生成payloads的代码进行了函数封装，并使cookies变成动态的
"""

import requests
from hashlib import md5
import random
import time

""" 加密部分的JS源码
var r = function(e) {
        var t = n.md5(navigator.appVersion)
          , r = "" + (new Date).getTime()
          , i = r + parseInt(10 * Math.random(), 10);
        return {
            ts: r,
            bv: t,
            salt: i,
            sign: n.md5("fanyideskweb" + e + i + "Y2FYu%TNSbMCxc3t2u^XT")
        }
    };
通过调试可知，e为输入的单词
"""


def generate_payloads(word):
    """根据要查询的单词生成payloads"""

    # 签名
    lts = str(int(time.time()*1000))        # 13位时间戳
    salt = lts + str(random.randint(0, 9))       # 其实可以在上一步直接*10000，whatever
    str1 = "fanyideskweb" + word + salt + "Y2FYu%TNSbMCxc3t2u^XT"
    md = md5()
    md.update(str1.encode())
    sign = md.hexdigest()

    # payloads
    data = {
        "i": word,
        "from": "AUTO",
        "to": "AUTO",
        "smartresult": "dict",
        "client": "fanyideskweb",
        "salt": salt,   # 13位时间戳加一位随机数
        "sign": sign,   # 签名
        "lts": lts,     # 13位时间戳
        "bv": "2c5a61877bd32cbd1c3db560d35de93d",   # 这个值可不变
        "doctype": "json",
        "version": "2.1",
        "keyfrom": "fanyi.web",
        "action": "FY_BY_REALTlME",
    }
    return data



if __name__ == "__main__":

    base_url = "https://fanyi.youdao.com/"  # 用来获取cookie
    url = "https://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 Edg/95.0.1020.44',
        'Referer': 'https://fanyi.youdao.com/',
    }


    # 获取cookies的一部分
    with requests.get(base_url, headers=headers) as res:
        cookies = res.cookies

    """最终提交的cookies如下
    cookies = {
        "OUTFOX_SEARCH_USER_ID": "123456789@123.123.123.123",
        "OUTFOX_SEARCH_USER_ID_NCOO": "123456789.123456",
        "JSESSIONID": "aaan231GYlTm9cUjwtl6x",  # JS ESSION ID
        "___rl__test__cookies": lts
    }
    """

    session = requests.session()
    while True:
        # 更新cookies：新增一个lts（测试发现可以和payloads中的不一样）
        lts = str(int(time.time()*1000))
        cookies.update({'___rl__test__cookies': lts})

        # 输入单词，并生成payload
        word = input("请输入要翻译的单词/段落：")
        data = generate_payloads(word)

        # 提交post请求
        with session.post(url, data=data, headers=headers, cookies=cookies) as res:
            result = res.json()

        # 打印结果
        for pars in result['translateResult']: # 不同段落
            print(pars[0]['tgt'])








