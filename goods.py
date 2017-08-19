#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2017/7/26 17:04
# @Author  : lingxiangxiang
# @File    : goods.py
import json

import requests
import sys
import time

def getchar():
    print 'Please press return key to continue'
    sys.stdin.read(1)

class Coupon:

    def __init__(self):
        pass

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
                #print(self.__AfterCouponPrice)
                #print(i['promoPrice'])

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

        #self.g_tk = 1915885660
        self.other_all_skuids = list()
        self.SkuidsList = list()
        self.otherSkuidsList = list()
        #self.GroupSkuids = list()
        self.SkuidsDict = list()
        self.__apptoken = apptoken

        # Update the first coupon lists
        self.updateFromCouponPromotion()
        self.SkuidsDict = self.GetSkuidsDict()

        # Update other lists
        self.updateFromHomeCouponPromotion()
        self.getOtherSkus()

    def updateFromCouponPromotion(self):

        #url = 'http://qwd.jd.com/fcgi-bin/qwd_actclassify_list?g_tk=1915885660&actid=10473'
        COUPON_PROMOTION_URL = 'http://qwd.jd.com/fcgi-bin/qwd_actclassify_list?g_tk={}&actid={}'

        g_tk = 1915885660
        actid = 10473

        r = requests.get(COUPON_PROMOTION_URL.format(g_tk, actid))
        print r.text

        obj = json.loads(r.text)
        objs = obj.pop('oItemList')

        for item in objs:
            ids = item.pop('skuIds')
            if 0 == len(ids):
                continue

            idlist = ids.split(',')
            self.SkuidsList.extend(idlist)

        print 'Retrieve', len(self.SkuidsList), 'SKUs'

    def updateFromHomeCouponPromotion(self):

        #url = 'http://qwd.jd.com/fcgi-bin/qwd_activity_list?g_tk=166988782&env=3'

        HOME_COUPON_PROMOTION_URL = 'http://qwd.jd.com/fcgi-bin/qwd_activity_list?g_tk={}&env={}'

        g_tk = 1915885660
        env = 3

        r = requests.get(HOME_COUPON_PROMOTION_URL.format(g_tk, env))
        print r.text

        obj = json.loads(r.text)
        objs = obj.pop('act')

        for item in objs:
            ids = item.pop('skuIds')
            if 0 == len(ids):
                continue

            idlist = ids.split(',')
            self.otherSkuidsList.extend(idlist)

        print 'Retrieve', len(self.otherSkuidsList), 'SKUs'

    def getOtherSkus(self):

        size = len(self.otherSkuidsList)

        GROUP_SIZE = 20

        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_2 like Mac OS X) AppleWebKit/603.2.4 (KHTML, like Gecko) Mobile/14F89 (4330609152);jdapp; JXJ/1.3.7.70717',
            'Referer': 'http://qwd.jd.com/goodslist.shtml?actId=10473&title=%E4%BC%98%E6%83%A0%E5%88%B8%E6%8E%A8%E5%B9%BF'}

        for index in range(1 + size/GROUP_SIZE):

            start = index * GROUP_SIZE
            end = start + GROUP_SIZE

            if end > size:
                end = size

            group = self.otherSkuidsList[start:end]
            print start, end, group
            #getchar()

            skus = '|'.join(group)
            url = 'http://qwd.jd.com/fcgi-bin/qwd_searchitem_ex?g_tk=166988782&skuid={0}'.format(skus)

            r = requests.get(url, headers=headers) #, cookies={'apptoken': self.__apptoken})
            obj = json.loads(r.text)
            skuObjs = obj.pop('sku')

            #print '-----------------------------------------'
            #print r.text
            #getchar()

            skus = ','.join(group)
            url = 'http://qwd.jd.com/fcgi-bin/qwd_discount_query?g_tk=166988782&vsku={0}'.format(skus)

            r = requests.get(url, headers=headers) #, cookies={'apptoken': self.__apptoken})
            obj = json.loads(r.text)
            discountSkuObjs = obj.pop('skulist')

            #print r.text
            #print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
            #getchar()

            for skuid in group:
                sku = Sku(skuid)
                sku.set_title_goodcom(skuObjs)

                if discountSkuObjs is not None:
                    sku.set_promoPrice(discountSkuObjs)

                #print sku.get_dict()
                #getchar()

                self.other_all_skuids.append(sku.get_dict())

    def GETLinks(self, group):
        '''获得20个商品的优惠券信息'''

        skus = ','.join(group)

        # referer 这个信息必须有，否则返回结果为空
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_2 like Mac OS X) AppleWebKit/603.2.4 (KHTML, like Gecko) Mobile/14F89 (4330609152);jdapp; JXJ/1.3.7.70717',
            'Referer': 'https://qwd.jd.com/goodslist.shtml?actId=10473&title=%E4%BC%98%E6%83%A0%E5%88%B8%E6%8E%A8%E5%B9%BF'}
        url = 'https://qwd.jd.com/fcgi-bin/qwd_coupon_query?g_tk=1915885660&sku={0}'.format(skus)
        res = requests.get(url=url, headers=headers, cookies={'apptoken': self.__apptoken})
        if len(res.text):
            data = json.loads(res.text)['data']
            if len(data):
                return data
        else:
            return None

    def GETTitle(self, group):

        '''获得20个商品的名字信息'''

        skus = '|'.join(group)

        # referer必须有，否则结果为空
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_2 like Mac OS X) AppleWebKit/603.2.4 (KHTML, like Gecko) Mobile/14F89 (4330609152);jdapp; JXJ/1.3.7.70717',
            'Referer': 'http://qwd.jd.com/goodslist.shtml?actId=10473&title=%E4%BC%98%E6%83%A0%E5%88%B8%E6%8E%A8%E5%B9%BF'}
        url = 'http://qwd.jd.com/fcgi-bin/qwd_searchitem_ex?g_tk=959337321&skuid={0}'.format(skus)
        res = requests.get(url=url, headers=headers, cookies={'apptoken': self.__apptoken})

        if len(res.text):
            data = json.loads(res.text)['sku']
            if len(data) > 0:
                return data
        else:
            return None

    def GetSkuidsDict(self):

        skuidsdict = list()

        size = len(self.SkuidsList)

        GROUP_SIZE = 20

        for index in range(1 + size/GROUP_SIZE):

            start = index * GROUP_SIZE
            end = start + GROUP_SIZE

            if end > size:
                end = size

            print start, end

            group = self.SkuidsList[start:end]

            # 获得优惠券的json信息
            link_json = self.GETLinks(group)
            # 获得名字的json信息
            title_json = self.GETTitle(group)

            '''
            if link_json is None or title_json is None:
                print group
                print link_json
                print title_json
                getchar()
            '''

            for skuid in group:

                sku = Sku(skuid)

                sku.set_link_price_couponprice(link_json)
                sku.set_title_goodcom(title_json)

                data = sku.get_dict()
                try:
                    if self.judge(data):
                        skuidsdict.append(data)
                        # print(data)
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

