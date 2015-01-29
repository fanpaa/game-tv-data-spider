# -*- coding: utf8 -*-
# 抓取游戏直播网站的房间资料
__author__ = 'fanpaa@gmail.com'
# ===>需要安装的库
import requests
import bs4
# <===
import re
import math
from multiprocessing import Pool
import json

www = {
    'douyu': 'http://www.douyutv.com',
    'zhanqi': 'http://www.zhanqi.tv',
    'huya': 'http://www.huya.com',
}


def print_arr(arr):
    lens = len(arr)
    for i in range(lens):
        print arr[i]['view'], arr[i]['zbName'], arr[i]['title'], arr[i]['up'], arr[i]['url'], arr[i]['thumb']


# ====> douyu
def douyu_getListNumber(number):
    count = math.ceil(number / 30.0)
    count = int(count)
    return [i * 30 for i in range(count)]


def douyu_detailList(lists):
    result = []
    for l in lists:
        item = {}
        item['url'] = www['douyu'] + l.select('a')[0].attrs.get('href')
        item['thumb'] = l.select('.lazy')[0].attrs.get('data-original')
        item['title'] = l.select('.title')[0].get_text()
        item['view'] = l.select('.view')[0].get_text()
        item['up'] = l.select('.nnt')[0].get_text()
        item['zbName'] = l.select('.zbName em')[0].get_text()
        result.append(item)
    return result


def douyu_getCollection(page=0):
    global www
    url = www['douyu'] + '/directory/all?offset=' + str(page) + '&limlit=30'
    r = requests.get(url)
    b = bs4.BeautifulSoup(r.text)
    result = []
    if page == 0:
        lists = b.select('#item_data li')
    else:
        lists = b.select('li')
    return douyu_detailList(lists)


def douyu_multiprocess(list_number):
    pool = Pool(8)
    urls = douyu_getListNumber(list_number)
    results = pool.map(douyu_getCollection, urls)

    lists = []
    for i in results:
        lists += i

    lists = lists[:list_number]
    print '===>douyu<==='
    return lists


# <==== douyu

# ====> zhanqi
def zhanqi_getListNumber(number):
    count = math.ceil(number / 30.0)
    return [i + 1 for i in range(int(count))]


def zhanqi_detailList(lists):
    result = []
    for l in lists:
        item = {}
        item['url'] = www['zhanqi'] + '/' + l['code']
        item['thumb'] = l['bpic']
        item['title'] = l['title']
        item['view'] = l['online']
        item['up'] = l['nickname']
        item['zbName'] = l['gameName']
        result.append(item)
    return result


def zhanqi_getCollection(page=1):
    global www
    url = www['zhanqi'] + '/api/static/live.hots/30-' + str(page) + '.json'
    r = requests.get(url).json()['data']['rooms']
    return zhanqi_detailList(r)


def zhanqi_multiprocess(list_number):
    pool = Pool(8)
    urls = zhanqi_getListNumber(list_number)
    results = pool.map(zhanqi_getCollection, urls)

    lists = []
    for i in results:
        lists += i

    lists = lists[:list_number]
    print '===>zhanqi<==='
    return lists


# <==== zhanqi

# ====> huya

def huya_hasKey(key, dict):
    if key in dict.keys():
        return dict[key]
    return 'null'


def huya_getCollection(list_number):
    global www
    url = www['huya'] + '/l'
    r = requests.get(url)
    b = bs4.BeautifulSoup(r.text)
    m = re.search('\[.*\]', b.select('script')[4].get_text()).group(0)
    ddata = json.loads(m)
    result = []
    for i in range(list_number):
        item = {}
        item['url'] = www['huya'] + '/' + huya_hasKey('privateHost', ddata[i])
        item['thumb'] = huya_hasKey('screenshot', ddata[i])
        item['title'] = huya_hasKey('introduction', ddata[i])
        item['view'] = huya_hasKey('totalCount', ddata[i])
        item['up'] = huya_hasKey('nick', ddata[i])
        item['zbName'] = huya_hasKey('gameFullName', ddata[i])
        result.append(item)

    print '===>huya<==='
    return result


# <==== huya


if __name__ == '__main__':
    list_number = 100
    _json = {}

    _json['douyu'] = douyu_multiprocess(list_number)

    _json['zhanqi'] = zhanqi_multiprocess(list_number)

    _json['huya'] = huya_getCollection(list_number)

    # 导出list.json文件
    print '......done......'
    f = open('list.json', 'w')
    f.write(json.dumps(_json))
    f.close()



