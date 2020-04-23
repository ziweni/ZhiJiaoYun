# /usr/bin/python3
# coding=utf-8

import os
import yaml
import json
import math
import time
import random

from ZhiJiao import ZhiJiao
from alive_progress import alive_bar
from Util import print_list, print_tree

if __name__ == "__main__":

    try:
        # 读取配置文件
        with open("config.yml", "r", encoding='utf-8') as f:
            data = f.read()
        # 加载配置文件
        config = yaml.safe_load(data)
    except IOError:
        print("❌ 初始化时出现错误：没找到配置文件！")
        exit(-1)
    except yaml.YAMLError as exc:
        print("❌ 初始化时出现错误：配置文件异常！")
        exit(-2)

    # 初始化网课操作对象
    obj = ZhiJiao()

    print("开始登陆……")
    # 先判断有没有缓存Cookie
    if os.path.exists("cookies.json"):
        with open("cookies.json", "r", encoding='utf-8') as f:
            js = f.read()
        # 设置 Cookies
        obj.set_cookie(js)

    # 取一下数据，查看 Cookies 是否有效
    if len(obj.s.cookies.items()) == 0 or not ('courseList' in obj.getCourseList()):
        # 清空Cookies
        obj.s.cookies.clear()
        # 登陆
        if obj.login_m(str(config['member']['user']), str(config['member']['pass'])):
            if config['saveCookies']:
                # 获取 Cookies
                ck = json.dumps(obj.s.cookies.items())
                # 保存到文件
                f = open("cookies.json", "w", encoding='utf-8')
                f.write(ck)
                f.close()
        else:
            print("登陆失败！")
            exit(-3)

    userId = obj.getUserInfo()['stuId']

    print("正在获取课程列表……")
    course = obj.getCourseList()['courseList']

    # 输出
    print_list(course)

    while True:
        # 异常输入判断
        try:
            # 要求输入
            id = int(input("课程id: "))
        except ValueError:
            print("您输入的数据不符合规范！")
            continue
        if id == -1:
            exit(0)
        if id >= len(course) or id < 0:
            print("课程id不存在！")
            continue
        break

    # 输出选中的课程名称
    print("\n<%s>" % course[id]['courseName'])

    # 获取课程目录
    cata = obj.getCourseCata(course[id]['courseOpenId'], course[id]['openClassId'])

    # 输出目录
    print_tree(cata)

    # 遍历目录
    for item in cata:
        # 查看是否完成
        if item['percent'] == 100:
            continue

        # 获取目录id
        moduleId = item['id']

        for items in item['data']:
            # 获取数据
            courseOpenId = course[id]['courseOpenId']
            openClassId = course[id]['openClassId']
            topicId = items['id']
            # 获取任务
            task = obj.getData(courseOpenId, openClassId, topicId)

            # 遍历任务点; 判断是否完成
            for item2 in task:
                # 判断是否达到100%的进度
                if item2['stuCellPercent'] == 100:
                    continue
                # 获取数据
                cellId = item2['Id']
                task_type = item2['categoryName']

                # 取任务详细信息
                info = obj.getTaskInfo(courseOpenId, openClassId, cellId, moduleId)

                # 判断多开
                if info['code'] == -100:
                    print("\n⚠️ 因服务器限制，您只可以同时学习一门课程！")
                    action = input("❓ 是否继续学习？(yes/no): ")
                    if action != "yes":
                        exit(0)
                    
                    # 告诉服务器我们的选择
                    obj.choiceCourse(courseOpenId, openClassId, cellId, moduleId, info['currCellName'])

                    # 重新获取数据
                    info = obj.getTaskInfo(courseOpenId, openClassId, cellId, moduleId)

                
                print("\n💼 任务类型: %s" % task_type)

                # 获取数据
                cellLogId = info['cellLogId']
                Token = info['guIdToken']

                if task_type == 'ppt':
                    print("📽 ppt 《%s》 \n⏳ 正在自动完成" % item2['cellName'])
                    pageCount = info['pageCount']
                    obj.updateLog(courseOpenId, openClassId, moduleId, cellId, cellLogId, pageCount, 0, pageCount, Token)
                    print("🎉 ppt任务完成!")
                elif task_type == '视频':

                    audioVideoLong = info['audioVideoLong']

                    print("📺 视频 《%s》 " % item2['cellName'])
                    print("⏰ 视频时长: %.2f 分钟" % (audioVideoLong / 60))
                    print("⏳ 正在自动完成……")

                    # 开始进行模拟上报数据
                    # 观看进度变量
                    index = 0
                    # 获取已观看的时间
                    times = info['stuStudyNewlyTime'] #20.2
                    # 进度条
                    with alive_bar(int(audioVideoLong) + 1) as bar:
                        while True:
                            # 如果是视频长度大于 10 秒
                            # 我们就分步走
                            # 首先先判断，我们之前是否有看过
                            if times > 0:
                                # 如果有看过, 就把原进度赋值过来
                                index = times
                                # 然后再将进度变化反馈给用户
                                for ited in range(int(index)):
                                    bar()
                                # 再把进度记录给置为 0 
                                # 以免之后的循环出现问题
                                times = 0

                            # 首先判断视频长度的是否 小于 10 秒, 或者 剩余的播放时间是否够 10 秒
                            if audioVideoLong > 10 and audioVideoLong - index > 10:
                                # 到这就说明视频长度既大于10秒，并且剩余的播放时间也大于10秒
                                # 然后就开始延时
                                for ited in range(10):
                                    bar()
                                    time.sleep(1)
                                # 延时后级对 index 进行递增 10
                                index = index + 10
                                # 然后设置一个用于告诉服务器播放进度对值
                                temp = index + random.random()
                            else:
                                # 不足1秒的按照1秒算
                                itemed = range(int(audioVideoLong - index) + 1)
                                for ited in itemed:
                                    bar()
                                    time.sleep(1)
                                # 然后直接赋值
                                temp = audioVideoLong
                            # 上报数据
                            res = obj.updateLog(courseOpenId, openClassId, moduleId, cellId, cellLogId, 0, "%.6f" % temp, 0, Token)

                            # 判断是否出现异常 或者 是否完成
                            if not res or temp == audioVideoLong: 
                                break
 
                    # 判断是否完成, 从循环出来只有可能是出现异常和正常
                    if not res:
                        print("🚫 该视频任务因数据上报异常而终止!")
                    else:
                        if config['videoComment']:
                            # 获取这个视频的评论列表
                            comment = obj.getComment(courseOpenId, openClassId, moduleId, cellId)
                    
                            exit = False

                            # 判断视频是否评论
                            for item4 in comment:
                                if item4['userId'] == userId:
                                    exit = True
                                    break
                        
                            # 判断是否评论
                            if not exit:

                                size = len(config['commentList'])

                                rand = random.randint(0, size - 1)

                                content = config['commentList'][rand]

                                star = config['videoStar']

                                # 执行评论
                                obj.commentVideo(courseOpenId, openClassId, cellId, moduleId, content, star)
                        
                        print("🎉 视频 《%s》 已完成!" % item2['cellName'])

                elif task_type == '链接':
                    print("🔗 链接 《%s》 已完成!" % item2['cellName'])
                elif task_type == '图片':
                    print("🖼 图片 《%s》 已完成!" % item2['cellName'])

    print("\n🎉 你已完成了本课的所有课程！")
