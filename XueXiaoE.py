# /usr/bin/python3
# coding=utf8

import re
import html
import json
import random
import base64
import hashlib
import requests
from urllib.parse import quote
from Util import get_timestamp, obj2str

"""
学小易操作类
用于搜题
"""

class XueXiaoE:

    s = requests.session()

    def __init__(self):
        # 设置全局Http协议头
        self.s.headers.update(
            {
                'Accept': "*/*",
                'Accept-Language': "zh-Hans-CN;q=1",
                'Connection': "keep-alive",
                'Accept-Encoding': "gzip, deflate, br",
                'User-Agent': "xueyi/1 CFNetwork/1121.2.2 Darwin/19.3.0"
            })

    def login_m(self, u_name, u_pass):

        uri = "https://app.51xuexiaoyi.com/api/v1/login"

        headers = {
            'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
            'Accept-Encoding': "gzip, deflate, br"
        }

        data = obj2str({
            'username': u_name,
            'password': u_pass
        })

        r = self.s.post(uri, headers=headers, data=data)

        res = json.loads(r.text)

        if res['code'] == 200:
            token = res['data']['api_token']
            self.s.headers.update({
                'token': token
            })

        return res['code'] == 200

    def searchCourse(self, key):

        uri = "https://app.51xuexiaoyi.com/api/v1/course/searchCourse"

        headers = {
            'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
            'Accept-Encoding': "gzip, deflate, br"
        }

        data = obj2str({
            'keyword': key
        }).encode(encoding="utf-8")

        r = self.s.post(uri, headers=headers, data=data)

        res = json.loads(r.text)

        if res['code'] != 200:
            return []

        return res['data']

    def searchQuestion(self, key, ids):

        uri = "https://app.51xuexiaoyi.com/api/v1/searchQuestion"

        headers = {
            'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
            'Accept-Encoding': "gzip, deflate, br"
        }

        data = obj2str({
            'keyword': key,
            'id': ids
        }).encode(encoding="utf-8")

        r = self.s.post(uri, headers=headers, data=data)

        res = json.loads(r.text)

        if res['code'] != 200:
            return []

        return res['data']