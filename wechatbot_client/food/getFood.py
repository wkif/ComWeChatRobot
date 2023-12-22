#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

import requests
from bs4 import BeautifulSoup

def getFood(index):
    # url = 'https://home.meishichina.com/show-top-type-recipe-page-' + str(index) + '.html'
    url = "https://home.meishichina.com/collect-6328734-page-"+str(index)+".html"
    # 添加请求头信息和Cookie
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        'Cookie': 'msc-user-sign-mark=1'
    }
    # 发送GET请求获取页面内容
    response = requests.get(url, headers=headers)

    # 检查响应状态码
    if response.status_code == 200:
        # 解析网页内容
        soup = BeautifulSoup(response.text, 'html.parser')
        # print(soup)
        # 获取所有被h2包裹的a标签的内容
        h2list = soup.findAll('h2')
        for h2_tag in h2list:
            a_tag = h2_tag.find('a')
            dish_name = a_tag.text.strip()
            print(dish_name)
        # a_tag = soup.findAll('a')
        # for a in a_tag:
        #     title = a.get('title')
        #     print(title)
    else:
        print('Failed to fetch the page:', response.status_code)

def main():
    for i in range(1, 17):
        getFood(i)
main()