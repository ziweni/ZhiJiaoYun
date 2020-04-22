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
职教云操作类
"""


class ZhiJiao:

    s = requests.session()

    def __init__(self):
        # 设置全局Http协议头
        self.s.headers.update(
            {
                'Accept': "*/*",
                'Accept-Language': "zh-Hans-CN;q=1",
                'Connection': "keep-alive",
                'Accept-Encoding': "gzip, deflate, br",
                'User-Agent': "yktIcve/2.8.21 (com.66ykt.66yktteacherzhihui; build:2020041004; iOS 13.3.1) Alamofire/4.7.3"
            })

    # 获取验证码: 保存到外部
    def get_code(self, name):
        uri = "https://zjy2.icve.com.cn/api/common/VerifyCode/index?t=%f" % random.random()

        r = self.s.get(uri)

        with open(name, 'wb') as fd:
            for chunk in r.iter_content():
                fd.write(chunk)

    # 执行登陆; Web网页接口
    def login(self, u_name, u_pass, code):

        uri = "https://zjy2.icve.com.cn/api/common/login/login"

        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': "https://zjy2.icve.com.cn",
            'Referer': "https://zjy2.icve.com.cn/portal/login.html"
        }

        data = obj2str({
            'userName': u_name,
            'userPwd': u_pass,
            'verifyCode': code
        })

        r = self.s.post(uri, headers=headers, data=data)

        ret = json.loads(r.text)
        return ret['code'] == 1

    # 执行登陆: Mobile端
    # 优点是可以免验证码登陆
    def login_m(self, u_name, u_pass):

        uri = "https://zjyapp.icve.com.cn/newMobileAPI/MobileLogin/newLogin"

        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'Accept-Encoding': 'gzip, deflate, br',
        }

        data = obj2str({
            'appVersion': "2.8.21",
            'clientId': "057386f8991f402498dfc38ed5cb7e49",
            'equipmentApiVersion': "14.1",
            'equipmentAppVersion': "2.8.21",
            'equipmentModel': "iPhone%2012",
            'sourceType': "3",
            'userName': u_name,
            'userPwd': u_pass
        })
        
        r = self.s.post(uri, headers=headers, data=data)

        ret = json.loads(r.text)
        return ret['code'] == 1

    # 验证码识别; 联众打码接口
    def code(self, imagePath):
        uri = "http://v1-http-api.jsdama.com/api.php?mod=php&act=upload"

        user_name = "******"
        user_pw = "******."

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
            'Connection': 'keep-alive',
            'Host': 'v1-http-api.jsdama.com',
            'Upgrade-Insecure-Requests': '1'
        }

        files = {
            'upload': (imagePath, open(imagePath, 'rb'), 'image/png')
        }

        data = {
            'user_name': user_name,
            'user_pw': user_pw,
            'yzm_type': '1001'
        }

        s = requests.session()
        r = s.post(uri, headers=headers,
                   data=data, files=files, verify=False)
        a = json.loads(r.text)

        return a['data']['val']

    # 设置Cookie
    def set_cookie(self, ck):
        obj = json.loads(ck)

        cookies = {}
        for o in obj:
            cookies[o[0]] = o[1]

        self.s.cookies.update(cookies)

    # 获取课程列表
    def getCourseList(self):

        uri = "https://zjy2.icve.com.cn/api/student/learning/getLearnningCourseList"

        r = self.s.post(uri)
        return json.loads(r.text)

    # 获取课程目录
    def getCourseCata(self, courseOpenId, openClassId):
        
        uri = "https://zjy2.icve.com.cn/api/study/process/getProcessList"

        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'Accept-Encoding': 'gzip, deflate, br',
        }

        # 获取一级目录
        r = self.s.post(uri, headers=headers, data=obj2str({
            'courseOpenId': courseOpenId,
            'openClassId': openClassId
        }))

        ret = json.loads(r.text)

        if ret['code'] != 1:
            raise Exception("获取目录时，出现异常!")

        length = len(ret['progress']['moduleList'])

        i = 0
        # 遍历 获取二级目录
        while i < length:

            item = ret['progress']['moduleList'][i]
            # 先进行判断
            # 看看是否是 100% 避免去获取已经完成的视频的二级目录
            if item['percent'] == 100:
                i = i + 1
                continue

            # 获取二级模块id
            moduleId = item['id']
            
            ret2 = self.getLevelCata(courseOpenId, moduleId)

            ret['progress']['moduleList'][i]['data'] = ret2['topicList']

            i = i + 1

        return ret['progress']['moduleList']

    def getLevelCata(self, courseOpenId, moduleId):
        
        uri = "https://zjy2.icve.com.cn/api/study/process/getTopicByModuleId"

        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'Accept-Encoding': 'gzip, deflate, br',
        }

        # 获取二级目录
        r = self.s.post(uri, headers=headers, data=obj2str({
            'courseOpenId': courseOpenId,
            'moduleId': moduleId
        }))

        ret = json.loads(r.text)

        if ret['code'] != 1:
            raise Exception("获取目录时，出现异常!")

        return ret

    # 获取二级目录的视频
    def getData(self, courseOpenId, openClassId, topicId):

        uri = "https://zjy2.icve.com.cn/api/study/process/getCellByTopicId"

        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'Accept-Encoding': 'gzip, deflate, br',
        }

        data = obj2str({
            'courseOpenId': courseOpenId,
            'openClassId': openClassId,
            'topicId': topicId
        })

        r = self.s.post(uri, headers=headers, data=data)

        ret = json.loads(r.text)

        if ret['code'] != 1:
                raise Exception("获取任务时，出现异常!")

        return ret['cellList']

    # 获取任务信息
    def getTaskInfo(self, courseOpenId, openClassId, cellId, moduleId):

        uri = "https://zjy2.icve.com.cn/api/common/Directory/viewDirectory"

        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'Accept-Encoding': 'gzip, deflate, br',
        }

        data = obj2str({
            'courseOpenId': courseOpenId,
            'openClassId': openClassId,
            'cellId': cellId,
            'flag': "s",
            'moduleId': moduleId
        })

        r = self.s.post(uri, headers=headers, data=data)

        return json.loads(r.text)

    # 上报任务完成状态
    def updateLog(self, courseOpenId, openClassId, moduleId, cellId, cellLogId, picNum, studyNewlyTime, studyNewlyPicNum, token):
        
        uri = "https://zjy2.icve.com.cn/api/common/Directory/stuProcessCellLog"

        headers = {
            'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
            'Accept-Encoding': "gzip, deflate, br",
            'Origin': "https://zjy2.icve.com.cn",
            'X-Requested-With': "XMLHttpRequest",
            'Referer': "https://zjy2.icve.com.cn/common/directory/directory.html?courseOpenId=%s&openClassId=%s&cellId=%s&flag=s&moduleId=%s" % (courseOpenId, openClassId, cellId, moduleId)
        }

        data = obj2str({
            'courseOpenId': courseOpenId,
            'openClassId': openClassId,
            'cellId': cellId,
            'cellLogId': cellLogId,
            'picNum': picNum,
            'studyNewlyTime': studyNewlyTime,
            'studyNewlyPicNum': studyNewlyPicNum,
            'token': token
        })

        r = self.s.post(uri, headers=headers, data=data)

        ret = json.loads(r.text)

        return ret['code'] == 1

    # 确认任务
    def choiceCourse(self, courseOpenId, openClassId, cellId, moduleId, cellName):

        uri = "https://zjy2.icve.com.cn/api/common/Directory/changeStuStudyProcessCellData"

        headers = {
            'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
            'Accept-Encoding': "gzip, deflate, br",
            'Origin': "https://zjy2.icve.com.cn",
            'X-Requested-With': "XMLHttpRequest",
            'Referer': "https://zjy2.icve.com.cn/common/directory/directory.html?courseOpenId=%s&openClassId=%s&cellId=%s&flag=s&moduleId=%s" % (courseOpenId, openClassId, cellId, moduleId)
        }

        data = obj2str({
            'courseOpenId': courseOpenId,
            'openClassId': openClassId,
            'cellId': cellId,
            'moduleId': moduleId,
            'cellName': cellName
        }).encode(encoding="utf-8")

        r = self.s.post(uri, headers=headers, data=data)

        ret = json.loads(r.text)
        return ret['code'] == 1
    
    # 取用户用户信息
    def getUserInfo(self):

        uri = "https://zjy2.icve.com.cn/api/student/Studio/index"

        r = self.s.post(uri)

        ret = json.loads(r.text)

        return ret

    # 获取视频评论
    def getComment(self, courseOpenId, openClassId, moduleId, cellId):

        uri = "https://zjy2.icve.com.cn/api/common/Directory/getCellCommentData"

        headers = {
            'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
            'Accept-Encoding': "gzip, deflate, br",
            'Origin': "https://zjy2.icve.com.cn",
            'X-Requested-With': "XMLHttpRequest",
            'Referer': "https://zjy2.icve.com.cn/common/directory/directory.html?courseOpenId=%s&openClassId=%s&cellId=%s&flag=s&moduleId=%s" % (courseOpenId, openClassId, cellId, moduleId)
        }

        data = obj2str({
            'courseOpenId': courseOpenId,
            'openClassId': openClassId,
            'cellId': cellId,
            'type': "0",
        })

        r = self.s.post(uri, headers=headers, data=data)

        ret = json.loads(r.text)

        if ret['code'] != 1:
            return []

        size = ret['pagination']['totalCount']

        if size <= 8:
            return ret['list']

        uri = "https://zjy2.icve.com.cn/common/Directory/getCellCommentData"

        listData = ret['list']

        index = 1

        while index * 8 < size:

            index = index + 1

            data = obj2str({
                'courseOpenId': courseOpenId,
                'openClassId': openClassId,
                'cellId': cellId,
                'type': "0",
                'pageSize': 8,
                'page': index
            })

            r = self.s.post(uri, headers=headers, data=data)

            ret = json.loads(r.text)

            for z in ret['list']:
                listData.insert(len(listData), z)

        return listData

    # 给视频课程进行评论
    def commentVideo(self, courseOpenId, openClassId, cellId, moduleId, content, star):

        uri = "https://zjy2.icve.com.cn/api/common/Directory/addCellActivity"

        headers = {
            'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
            'Accept-Encoding': "gzip, deflate, br",
            'Origin': "https://zjy2.icve.com.cn",
            'X-Requested-With': "XMLHttpRequest",
            'Referer': "https://zjy2.icve.com.cn/common/directory/directory.html?courseOpenId=%s&openClassId=%s&cellId=%s&flag=s&moduleId=%s" % (courseOpenId, openClassId, cellId, moduleId)
        }

        data = obj2str({
            'courseOpenId': courseOpenId,
            'openClassId': openClassId,
            'cellId': cellId,
            'content': content,
            'docJson': "",
            'star': star,
            'activityType': 1
        }).encode(encoding="utf-8")

        r = self.s.post(uri, headers=headers, data=data)

        ret = json.loads(r.text)

        return ret['code'] == 1
