#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
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

    async def WeiBoHotApi(self):
        url = "https://api.gumengya.com/Api/WeiBoHot"
        params = {
            "format": "json",
        }
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

    async def KfcApi(self):
        url = "https://api.khkj6.com/kfc/"
        params = {
            "format": "json",
        }
        r = http.request("GET", url, fields=params)
        content = r.data.decode("utf-8")
        if content:
            try:
                res = json.loads(content)
                if "msg" in res:
                    return res["msg"]
                else:
                    return "请求失败"
            # 状态码 200 表示请求成功
            # if (res['code'] == 200):
            #     c['text']
            # else:
            #     return "请求失败"
            except Exception:
                return "解析结果异常"
        else:
            # 无法获取返回内容，请求异常
            return "请求异常,老大你哪找的辣鸡接口，挂啦！"

    async def MoyuApi(self):
        url = "https://dayu.qqsuu.cn/moyuribao/apis.php?type=json"
        r = http.request("GET", url)
        content = r.data.decode("utf-8")
        if content:
            try:
                res = json.loads(content)
                # 状态码 200 表示请求成功
                if res["code"] == 200:
                    r = http.request("GET", res["data"])
                    imagePath = os.path.join(os.getcwd(), "file_cache/image")
                    if not os.path.exists(imagePath):
                        os.makedirs(imagePath)
                    file_path = os.path.join(imagePath, "moyu.jpg")
                    data = r.data
                    with open(file_path, mode="wb") as f:
                        f.write(data)
                    return file_path
                else:
                    return "请求失败"
            except Exception:
                return "解析结果异常"
        else:
            # 无法获取返回内容，请求异常
            return "请求异常,老大你哪找的辣鸡接口，挂啦！"

    async def NewsApi(self):
        url = "https://dayu.qqsuu.cn/weiyujianbao/apis.php"
        r = http.request("GET", url)
        content = r.data
        path = os.path.join(os.getcwd(), "file_cache/image/news.png")
        with open(path, "wb") as file:
            file.write(content)
        return path

    async def xingzuoyunshi(self):
        url = "https://dayu.qqsuu.cn/xingzuoyunshi/apis.php"
        r = http.request("GET", url)
        content = r.data
        path = os.path.join(os.getcwd(), "file_cache/image/xingzuoyunshi.png")
        with open(path, "wb") as file:
            file.write(content)
        return path
    # 吃什么
    async def eat(self):
        url = "https://api.52vmy.cn/api/wl/s/eat"
        r = http.request("GET", url)
        content = r.data.decode("utf-8")
        if content:
            try:
                res = json.loads(content)
                # 状态码 200 表示请求成功
                if res["code"] == 200:
                    return res["data"]
                else:
                    return "请求失败"
            except Exception:
                return "解析结果异常"
        else:
            # 无法获取返回内容，请求异常
            return "请求异常,老大你哪找的辣鸡接口，挂啦！"
    # 舔狗日记
    async def tongueDogDiary(self):
        url = "https://api.52vmy.cn/api/wl/yan/tiangou"
        r = http.request("GET", url)
        content = r.data.decode("utf-8")
        if content:
            try:
                res = json.loads(content)
                return res["content"]
            except Exception:
                return "解析结果异常"
        else:
            # 无法获取返回内容，请求异常
            return "请求异常,老大你哪找的辣鸡接口，挂啦！"  


