#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib3
import json
import random

http = urllib3.PoolManager()


async def TodayApi():
    url = 'https://api.52vmy.cn/api/wl/today'
    r = http.request('GET', url)
    content = r.data.decode('utf-8')
    if (content):
        try:
            res = json.loads(content)
            # 状态码 200 表示请求成功
            if (res['code'] == 200):
                data = res['data']
                length = len(data)
                index = random.randint(0, length)
                res = "--------------\n历史上的今天："+data[index]['year'] +\
                    "," + data[index]['title'] +\
                    "\n--------------\n"
                return res
            else:
                return "请求失败"
        except Exception:
            return "解析结果异常"
    else:
        # 无法获取返回内容，请求异常
        return "请求异常,老大你哪找的辣鸡接口，挂啦！"


# TodayApi()