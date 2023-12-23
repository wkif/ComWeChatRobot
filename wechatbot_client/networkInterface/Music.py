#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib3
import json

http = urllib3.PoolManager()


async def MusicApi(name):
    url = 'https://api.gumengya.com/Api/Music'
    params = {
        "format": "json",
        'text': name,
        'site': 'kugou',
        'page': '1',
    }
    r = http.request('GET', url, fields=params)
    content = r.data.decode('utf-8')
    if (content):
        try:
            res = json.loads(content)
            # 状态码 200 表示请求成功
            if (res['code'] == 200):
                data = res['data']
                if len(data) >= 1:
                    return data[0]
                else:
                    return "没搜到嘞"
            else:
                return "请求失败"
        except Exception:
            return "解析结果异常"
    else:
        # 无法获取返回内容，请求异常
        return "请求异常,老大你哪找的辣鸡接口，挂啦！"


# MusicApi("七秒钟的记忆")