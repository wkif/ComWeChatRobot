#!/usr/bin/python
# -*- coding: utf-8 -*-

import base64
import os
import urllib3
import json

http = urllib3.PoolManager()


async def NewsApi():
    url = 'https://zj.v.api.aa1.cn/api/60s-v2/?cc=kif秘书'
    r = http.request('GET', url)
    content = r.data
    print(type(content))
    # return content
# 将二进制数据写入文件
    path = os.path.join(os.getcwd(), "file_cache/temp/news.png")
    with open(path, "wb") as file:
        file.write(content)
        print("File saved successfully")
# NewsApi()
