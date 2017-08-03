#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2017/7/26 16:05
# @Author  : lingxiangxiang
# @File    : module.py
import json

import requests


class WARES():


    def __init__(self):
        self.SkuidsList = list()
        self.SkuidsStr = ''

    def get_skuids(self):

        url = 'http://qwd.jd.com/fcgi-bin/qwd_actclassify_list?g_tk=1915885660&actid=10473'

        s = requests.Session()
        r = s.get(url)
        html = r.text
        text = json.loads(html)
        for ids in text['oItemList']:
            print(ids['skuIds'])
            self.SkuidsStr = ',' + ids['skuIds'] + self.SkuidsStr

        self.SkuidsList = self.SkuidsStr.split(',')[1:]
