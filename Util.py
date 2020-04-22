# /usr/bin/python3
# coding=utf8

"""
工具集
"""

import time

# 获取时间戳
def get_timestamp():
    timestamp = time.time()
    return int(timestamp * 1000)

# json转字符
def obj2str(obj):
    ret = ""
    for key in obj:
        if ret == "":
            ret = key + "=" + str(obj[key])
        else:
            ret = ret + "&" + key + "=" + str(obj[key])
    return ret

def print_list(obj):
    if len(obj) == 0:
        return
    print("------------------------------------")
    print("│ id | 课程名称")
    index = 0
    for item in obj:
        print("| %2d | %-s  %d%%" % (index, item['courseName'], item['process']))
        index = index + 1
    print("------------------------------------")
    print("| 退出请输入 -1")
    print("------------------------------------")

def print_tree(obj):
    if len(obj) == 0:
        return

    oc = 0

    index = 0
    for item in obj:
        if item['percent'] != 100:
            c = "❌ [{0} %]".format(item['percent'])
        else:
            c = "✅ [{0} %]".format(item['percent'])
        
        if index == 0:
            print("┌ %s %s" % (item['name'], c))
        elif index == len(obj) - 1:
            print("└ %s %s" % (item['name'], c))
        else:
            print("├ %s %s" % (item['name'], c))

        if item['percent'] == 100:
            index = index + 1
            continue

        index2 = 0
        for item2 in item['data']:

            if index + 1 == len(obj):
                if len(item['data']) - 1 != index2:
                    print("  ├ %s" % item2['name'])
                else:
                    print("  └ %s" % item2['name'])
            else:
                if len(item['data']) - 1 != index2:
                    print("│ ├ %s" % item2['name'])
                else:
                    print("│ └ %s" % item2['name'])

            index2 = index2 + 1

        index = index + 1