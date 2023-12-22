#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib3
import json

http = urllib3.PoolManager()


async def getYiYanApi():
    url = 'https://api.gumengya.com/Api/YiYan'
    params = {
        'format': 'json',
    }
    r = http.request('GET', url, fields=params)
    content = r.data.decode('utf-8')
    if (content):
        try:
            res = json.loads(content)
            # 状态码 200 表示请求成功
            if (res['code'] == 200):
                return res['data']['text']
            else:
                return "请求失败"
        except Exception:
            return "解析结果异常"
    else:
        # 无法获取返回内容，请求异常
        return "请求异常,老大你哪找的辣鸡接口，挂啦！"
