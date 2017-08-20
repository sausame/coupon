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
        self.SkuidsDict = list()

        self.updateFromCouponPromotion()
        self.updateFromDiscountPromotion()

    def updateFromCouponPromotion(self):

        skuIds = self.getFromCouponPromotion()
        self.SkuidsDict = self.updateSkuList(skuIds, isCoupon=True)

    def updateFromDiscountPromotion(self):

        skuIds = self.getFromDiscountPromotion()
        self.other_all_skuids = self.updateSkuList(skuIds, isDiscount=True)

    def getFromCouponPromotion(self):

        skuIds = list()

        COUPON_PROMOTION_URL = 'http://qwd.jd.com/fcgi-bin/qwd_actclassify_list?g_tk={}&actid={}'

        G_TK = 1915885660
        actid = 10473

        r = requests.get(COUPON_PROMOTION_URL.format(G_TK, actid))

        obj = json.loads(r.text)
        objs = obj.pop('oItemList')

        ids = list()

        for item in objs:
            ids = item.pop('skuIds')
            if 0 == len(ids):
                continue

            idlist = ids.split(',')
            skuIds.extend(idlist)

        print 'Retrieve', len(skuIds), 'SKUs'
        return skuIds

    def getFromDiscountPromotion(self):

        skuIds = list()

        HOME_COUPON_PROMOTION_URL = 'http://qwd.jd.com/fcgi-bin/qwd_activity_list?g_tk={}&env={}'

        G_TK = 1915885660
        env = 3

        r = requests.get(HOME_COUPON_PROMOTION_URL.format(G_TK, env))

        obj = json.loads(r.text)
        objs = obj.pop('act')

        for item in objs:
            uniqueId = item.pop('uniqueId')
            ids = item.pop('skuIds')
            if 0 == len(ids):
                continue

            idlist = ids.split(',')
            skuIds.extend(idlist)

        print 'Retrieve', len(skuIds), 'SKUs'
        return skuIds

    def updateSkuList(self, skuIds, isCoupon=False, isDiscount=False):

        skus = list()

        size = len(skuIds)

        GROUP_SIZE = 20

        for index in range(1 + size/GROUP_SIZE):

            start = index * GROUP_SIZE
            end = start + GROUP_SIZE

            if end > size:
                end = size

            group = skuIds[start:end]

            basicInfors = self.searchItem(group)

            if isCoupon:
                extraInfors = self.searchCoupon(group)
            elif isDiscount:
                extraInfors = self.searchDiscount(group)

            print '-->', (end - start), len(basicInfors), len(extraInfors), group

            for skuid in group:

                sku = Sku(skuid)

                sku.set_title_goodcom(basicInfors)

                if isCoupon:
                    sku.set_link_price_couponprice(extraInfors)
                elif isDiscount:
                    sku.set_promoPrice(extraInfors)

                data = sku.get_dict()
                skus.append(data)
                '''
                try:
                    if self.judge(data):
                        skus.append(data)
                except Exception as e:
                    print e, data
                    getchar()
                '''

        return skus

    def updateGetSkuidsDict(self):

        skuidsdict = list()

        size = len(self.SkuidsList)

        GROUP_SIZE = 20

        for index in range(1 + size/GROUP_SIZE):

            start = index * GROUP_SIZE
            end = start + GROUP_SIZE

            if end > size:
                end = size

            group = self.SkuidsList[start:end]

            # 获得优惠券的json信息
            link_json = self.searchCoupon(group)

            # 获得名字的json信息
            title_json = self.searchItem(group)

            print '-->', (end - start), len(link_json), len(title_json)

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

    def getOtherSkus(self):

        size = len(self.otherSkuidsList)

        GROUP_SIZE = 20

        for index in range(1 + size/GROUP_SIZE):

            start = index * GROUP_SIZE
            end = start + GROUP_SIZE

            if end > size:
                end = size

            group = self.otherSkuidsList[start:end]
            print start, end, group

            skuObjs = self.searchItem(group)
            discountSkuObjs = self.searchDiscount(group)

            # Sometimes, searchitem doesn't return all items
            print '---->', len(skuObjs), len(discountSkuObjs), len(group)

            for skuid in group:
                for sku in skuObjs:
                    if skuid == sku['skuid']:
                        break
                else:
                    print 'Can not find', skuid, 'in searching'

                for sku in discountSkuObjs:
                    if skuid == sku['skuid']:
                        break
                else:
                    print 'Can not find', skuid, 'in discount'

            for skuid in group:
                sku = Sku(skuid)
                sku.set_title_goodcom(skuObjs)

                if discountSkuObjs is not None:
                    sku.set_promoPrice(discountSkuObjs)

                #print sku.get_dict()
                #getchar()

                self.other_all_skuids.append(sku.get_dict())

    def querySkuList(self, separator, templateUrl, listTagName, itemIds=None, itemId=None):

        if itemIds is not None:
            ids = separator.join(itemIds)
        elif itemId is not None:
            ids = itemId
        else:
            raise TypeError('Id or Ids can be all None')

        USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_2 like Mac OS X) AppleWebKit/603.2.4 (KHTML, like Gecko) Mobile/14F89 (4330609152);jdapp; JXJ/1.3.7.70717'
        REFERER = 'http://qwd.jd.com/goodslist.shtml?actId=10473&title=%E4%BC%98%E6%83%A0%E5%88%B8%E6%8E%A8%E5%B9%BF'

        G_TK = 959337321

        # Referer is needed
        headers = {'User-Agent': USER_AGENT, 'Referer': REFERER}
        url = templateUrl.format(G_TK, ids)
        r = requests.get(url, headers=headers)

        # TODO: add other judgement for http response

        # Error code
        obj = json.loads(r.text)
        errCode = int(obj.pop('errCode'))

        if errCode is not 0:
            print 'Response of', url, 'is', r.text
            return []

        return obj.pop(listTagName)

    def searchCoupon(self, itemIds=None, itemId=None):
        SEARCH_COUPON_URL_TEMPLATE = 'https://qwd.jd.com/fcgi-bin/qwd_coupon_query?g_tk={}&sku={}'
        return self.querySkuList(',', SEARCH_COUPON_URL_TEMPLATE, 'data', itemIds=itemIds, itemId=itemId)

    def searchItem(self, itemIds=None, itemId=None):
        SEARCH_ITEM_URL_TEMPLATE = 'http://qwd.jd.com/fcgi-bin/qwd_searchitem_ex?g_tk={}&skuid={}'
        return self.querySkuList('|', SEARCH_ITEM_URL_TEMPLATE, 'sku', itemIds=itemIds, itemId=itemId)

    def searchDiscount(self, itemIds=None, itemId=None):
        SEARCH_DISCOUNT_URL_TEMPLATE = 'http://qwd.jd.com/fcgi-bin/qwd_discount_query?g_tk={}&vsku={}'
        return self.querySkuList(',', SEARCH_DISCOUNT_URL_TEMPLATE, 'skulist', itemIds=itemIds, itemId=itemId)

    @staticmethod
    def judge(data):
        if int(data['goodCom']) < 300:
            return False
        if int(data['salecount']) < 300:
            return False
        if int(data['validEndTime']) < int(time.time() * 1000):
            return False
        return True

