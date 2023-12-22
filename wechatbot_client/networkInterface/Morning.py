#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib3

http = urllib3.PoolManager()


async def MorningApi():
    url = 'https://api.lolimi.cn/API/image-zw/'
    r = http.request('GET', url)
    content = r.data
    if (content):
        return content
    else:
        # 无法获取返回内容，请求异常
        return "请求异常,老大你哪找的辣鸡接口，挂啦！"


# if __name__ == '__main__':
#     print(MorningApi())