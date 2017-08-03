#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2017/7/26 17:04
# @Author  : lingxiangxiang
# @File    : goods.py
import json

import requests
import time


class Sku():

    def __init__(self, skuid):
        self.__skuid = skuid
        self.__link = ''
        self.__CouponPrice = float()
        self.__Price = float()
        self.__AfterCouponPrice = float()
        self.__title = ''
        self.__goodCom = ''
        self.__salecount = int()
        self.__skuimgurl = ''
        self.__linkstarttime = ''
        self.__linkendtime = ''


    def set_link_price_couponprice(self, link_json):
        '''获得sku的优惠券link， 价格price， 优惠券价格couponprice， 购买价aftercouponprice'''
        for ware in link_json:
            if self.__skuid == ware['skuId']:
                self.__link = ware['link']
                self.__Price = ware['quota']
                self.__CouponPrice = ware['denomination']
                self.__AfterCouponPrice = float(float(self.__Price) - float(self.__CouponPrice))
                self.__linkstarttime = ware['validBeginTime']
                self.__linkendtime = ware['validEndTime']

    def set_promoPrice(self, link_json):
        for i in link_json:
            if self.__skuid == i['skuid']:
                self.__AfterCouponPrice = i['promoPrice']
                print(self.__AfterCouponPrice)
                print(i['promoPrice'])

    def set_title_goodcom(self, title_json):
        '''获得sku的名字， 好评数'''
        for title in title_json:
            if self.__skuid == title['skuid']:
                self.__title = title['title']
                self.__goodCom = title['goodCom']
                self.__salecount = title['salecount']
                self.__skuimgurl = title['skuimgurl']
                self.__Price = title['price']



    def get_dict(self):
        # 把sku转换成字典
        skudict = {}
        skudict['skuid'] = self.__skuid
        skudict['link'] = self.__link
        skudict['CouponPrice'] = self.__CouponPrice
        skudict['Price'] = self.__Price
        skudict['AfterCouponPrice'] = self.__AfterCouponPrice
        skudict['title'] = self.__title
        skudict['goodCom'] = self.__goodCom
        skudict['salecount'] = self.__salecount
        skudict['skuimgurl'] = self.__skuimgurl
        skudict['validBeginTime'] = self.__linkstarttime
        skudict['validEndTime'] = self.__linkendtime
        return skudict







class SkuManager():

    def __init__(self, apptoken):
        self.other_all_skuids = list()
        self.SkuidsList = list()
        self.SkuidsStr = ''
        self.GroupSkuids = list()
        self.SkuidsDict = list()
        self.__apptoken = apptoken
        self.get_skuids()
        self.GroupSkuids = self.GetGroupSkuids(self.SkuidsList)
        self.SkuidsDict = self.GetSkuidsDict()
        for uid in self.UniqueId():
            self.other_all_skuids += self.get_other_skuids(uid)

    def UniqueId(self):
        '''获得京享街首页上所有的商品skuid'''

        uniqueId = list()
        url = 'http://qwd.jd.com/fcgi-bin/qwd_activity_list?g_tk=166988782&env=3'
        s = requests.session()
        r = s.get(url)
        html = r.text
        text = json.loads(html)['act']
        for act in text:
            if len(act['skuIds']) >= 1:
                uniqueId.append(act['uniqueId'])
        print('#################################uniqueId')
        print(uniqueId)
        return uniqueId

    def get_other_skuids(self, uniqueId):
        other_all_skuids = list()
        url1 = 'http://qwd.jd.com/fcgi-bin/qwd_activity_list?g_tk=166988782&actid={0}'.format(uniqueId)

        s = requests.Session()
        r = s.get(url1)
        html = r.text
        # 首先获得每个actid所对应的skuids
        text = json.loads(html)
        if len(text['act']) > 0:
            replace_list = text['act'][0]['skuIds'].split(',')
            print('###################uniqueId = {0}    len(replace_list) = {1}'.format(uniqueId, len(replace_list)))
        # replace_list 就是我们所得到所有的skuids
        # 然后每20个元素进行分组
        group_list = self.GetGroupSkuids(replace_list)
        for group in group_list:
            text_str = self.ChangeTitle(group)
            text_discount = self.ChangeLink(group)
            url2 = 'http://qwd.jd.com/fcgi-bin/qwd_searchitem_ex?g_tk=166988782&skuid={0}'.format(text_str)
            url3 = 'http://qwd.jd.com/fcgi-bin/qwd_discount_query?g_tk=166988782&vsku={0}'.format(text_discount)
            res2 = s.get(url2).text
            res3 = s.get(url3).text
            skuidlist = json.loads(res2)['sku']
            if json.loads(res3)['skulist']:
                skulist = json.loads(res3)['skulist']
                for i in skuidlist:
                    sku = Sku(i['skuid'])
                    sku.set_title_goodcom(skuidlist)
                    sku.set_promoPrice(skulist)
                    other_all_skuids.append(sku.get_dict())
            else:
                for i in skuidlist:
                    sku = Sku(i['skuid'])
                    sku.set_title_goodcom(skuidlist)
                    # sku.set_promoPrice(skulist)
                    other_all_skuids.append(sku.get_dict())
        return other_all_skuids




    def get_skuids(self):

        url = 'http://qwd.jd.com/fcgi-bin/qwd_actclassify_list?g_tk=1915885660&actid=10473'

        s = requests.Session()
        r = s.get(url)
        html = r.text
        text = json.loads(html)
        for ids in text['oItemList']:
            # print(ids['skuIds'])
            self.SkuidsStr = ',' + ids['skuIds'] + self.SkuidsStr

        self.SkuidsList = self.SkuidsStr.split(',')[1:]
        print('###################################################')
        print(len(self.SkuidsList))
        print('###################################################')

    def GetGroupSkuids(self, skuidslist):
        groupskuids = list()
        if len(skuidslist) % 20 == 0:
            m = len(skuidslist)/20
        else:
            m = len(skuidslist)/20 + 1
        for i in xrange(0, m):
            groupskuids.append(skuidslist[i*20:(i+1)*20])
        return groupskuids

    def ChangeLink(self, group):
        '''把list转换成字符串，以便在http中传入参数使用'''
        sku_str = ''
        for sku in group:
            sku_str = sku + ',' + sku_str
        return sku_str[:-1]

    def ChangeTitle(self, group):
        '''把list转换成以|连接，以便在http中传入参数使用'''
        sku_str = ''
        for sku in group:
            sku_str = sku + '|' + sku_str
        return sku_str[:-1]


    def GETLinks(self, group_str):
        '''获得20个商品的优惠券信息'''

        # referer 这个信息必须有，否则返回结果为空
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_2 like Mac OS X) AppleWebKit/603.2.4 (KHTML, like Gecko) Mobile/14F89 (4330609152);jdapp; JXJ/1.3.7.70717',
            'Referer': 'https://qwd.jd.com/goodslist.shtml?actId=10473&title=%E4%BC%98%E6%83%A0%E5%88%B8%E6%8E%A8%E5%B9%BF'}
        url = 'https://qwd.jd.com/fcgi-bin/qwd_coupon_query?g_tk=1915885660&sku={0}'.format(group_str)
        res = requests.get(url=url, headers=headers, cookies={'apptoken': self.__apptoken})
        if len(res.text):
            data = json.loads(res.text)['data']
            if len(data):
                return data
        else:
            return None

    def GETTitle(self, group_str):

        '''获得20个商品的名字信息'''

        # referer必须有，否则结果为空
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_2 like Mac OS X) AppleWebKit/603.2.4 (KHTML, like Gecko) Mobile/14F89 (4330609152);jdapp; JXJ/1.3.7.70717',
            'Referer': 'http://qwd.jd.com/goodslist.shtml?actId=10473&title=%E4%BC%98%E6%83%A0%E5%88%B8%E6%8E%A8%E5%B9%BF'}
        url = 'http://qwd.jd.com/fcgi-bin/qwd_searchitem_ex?g_tk=959337321&skuid={0}'.format(group_str)
        res = requests.get(url=url, headers=headers, cookies={'apptoken': self.__apptoken})

        if len(res.text):
            data = json.loads(res.text)['sku']
            if len(data) > 0:
                return data
        else:
            return None
    def GetSkuidsDict(self):
        skuidsdict = list()
        for group in self.GroupSkuids:
            # 把20个元素的列表转换成字符串
            group_link = self.ChangeLink(group)
            # 把20个元素搞成|相连接
            group_title = self.ChangeTitle(group)
            # 获得优惠券的json信息
            link_json = self.GETLinks(group_link)
            # 获得名字的json信息
            title_json =  self.GETTitle(group_title)
            for i in xrange(len(group)):
                sku = Sku(group[i])
                sku.set_link_price_couponprice(link_json)
                sku.set_title_goodcom(title_json)
                data = sku.get_dict()
                try:
                    if self.judge(data):
                        skuidsdict.append(data)
                        # print(data)
                # skuidsdict.append(sku.get_dict())
                except Exception as e:
                    print data
        return skuidsdict

    @staticmethod
    def judge(data):
        if int(data['goodCom']) < 300:
            return False
        if int(data['salecount']) < 300:
            return False
        if int(data['validEndTime']) < int(time.time() * 1000):
            return False
        return True

