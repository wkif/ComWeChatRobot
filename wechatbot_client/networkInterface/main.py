#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib3
import json

http = urllib3.PoolManager()


class NetworkInterface:

    async def WeatherApi(self, city):
        url = "https://api.gumengya.com/Api/Weather"
        params = {"format": "json", "city": city, "scene": "1"}
        r = http.request("GET", url, fields=params)
        content = r.data.decode("utf-8")
        if content:
            try:
                res = json.loads(content)
                # 状态码 200 表示请求成功
                if res["code"] == 200:
                    return res
                else:
                    return "请求失败"
            except Exception:
                return "解析结果异常"
        else:
            # 无法获取返回内容，请求异常
            return "请求异常,老大你哪找的辣鸡接口，挂啦！"

    async def getDouYinWaterMarkApi(self, douyinurl):
        url = "https://tenapi.cn/v2/video"
        params = {
            "url": douyinurl,
        }
        r = http.request("GET", url, fields=params)
        content = r.data.decode("utf-8")
        if content:
            try:
                res = json.loads(content)
                print(res)
                # 状态码 200 表示请求成功
                if res["code"] == 200:
                    return res
                else:
                    return "哦豁，没弄到视频"
            except Exception:
                return "解析结果异常"
        else:
            # 无法获取返回内容，请求异常
            return "请求异常,老大你哪找的辣鸡接口，挂啦！"
