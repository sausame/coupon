#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import random
import requests
import time

from base import Sku, Coupon, Discount

class SkuManagerBase:

    def __init__(self, configFile, db):
        self.configFile = configFile
        self.db = db

        self.skuIdList = None
        self.newSkuIdList = None

    def update(self):
        raise TypeError('No implement')

    def updateDb(self, tableName, skuIdList):

        if skuIdList is None or len(skuIdList) == 0:
            return

        sql = ''' SELECT COUNT(*) AS num FROM `{}`
                  WHERE skuid NOT IN ({}) '''.format(tableName, ', '.join(skuIdList))
        result = self.db.query(sql)

        for row in result:
            print 'Delete', row['num'], 'records in', tableName

        sql = ''' DELETE FROM `{}`
                  WHERE skuid NOT IN ({}) '''.format(tableName, ', '.join(skuIdList))
        self.db.query(sql)

    def searchSkuList(self, separator, templateUrl, listTagName, itemIds=None, itemId=None):

        if itemIds is not None:
            ids = separator.join(itemIds)
        elif itemId is not None:
            ids = itemId
        else:
            raise TypeError('Id or Ids can be all None')

        USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_2 like Mac OS X) AppleWebKit/603.2.4 (KHTML, like Gecko) Mobile/14F89 (4330609152);jdapp; JXJ/1.3.7.70717'
        REFERER = 'http://qwd.jd.com/goodslist.shtml?actId=10473&title=%E4%BC%98%E6%83%A0%E5%88%B8%E6%8E%A8%E5%B9%BF'

        #G_TK = 959337321
        G_TK = 1915885660

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

    def search(self, itemIds=None, itemId=None):
        raise TypeError('No implement')

    def getSkuId(self, param):
        raise TypeError('No implement')

    def create(self, param):
        raise TypeError('No implement')

    def retrieveSkuList(self, skuIds):

        if skuIds is None:
            return None

        GROUP_SIZE = 20
        size = len(skuIds)

        newSkuIds = list()
        actualSkuIds = list()

        skuList = list()

        for index in range(1 + size/GROUP_SIZE):

            start = index * GROUP_SIZE
            end = start + GROUP_SIZE

            if start >= size:
                break

            if end > size:
                end = size

            group = skuIds[start:end]

            paramList = self.search(group)

            if paramList is not None:
                for param in paramList:

                    skuid = self.getSkuId(param)

                    actualSkuIds.append(skuid)

                    for i in range(len(group)):
                        if skuid == group[i]:
                            del(group[i])
                            break
                    else:
                        print 'An alien:\n', param

                    sku = self.create(param)

                    if sku is not None:
                        newSkuIds.append(skuid)
                        skuList.append(sku)
                else:
                    if len(group) > 0:
                        print 'No matches:', group

            print (end - start), len(paramList), len(skuList)

            # Sleep for a while
            time.sleep(1.0 + random.random())

        return skuList, actualSkuIds, newSkuIds

class SkuManager(SkuManagerBase):

    def __init__(self, configFile, db):

        SkuManagerBase.__init__(self, configFile, db)

    def search(self, itemIds=None, itemId=None):
        SEARCH_ITEM_URL_TEMPLATE = 'http://qwd.jd.com/fcgi-bin/qwd_searchitem_ex?g_tk={}&skuid={}'
        return self.searchSkuList('|', SEARCH_ITEM_URL_TEMPLATE, 'sku', itemIds=itemIds, itemId=itemId)

    def getSkuId(self, param):
        return param['skuid']

    def create(self, param):

        if self.db.findOne('SkuTable', skuid=self.getSkuId(param)):
            # Already exists
            return None

        sku = Sku(param)
        sku.insert(self.db, 'SkuTable')

        return sku

    def update(self, skuIds):
        self.updateDb('SkuTable', skuIds)

class CouponManager(SkuManagerBase):

    def __init__(self, configFile, db):
        SkuManagerBase.__init__(self, configFile, db)

    def search(self, itemIds=None, itemId=None):
        SEARCH_COUPON_URL_TEMPLATE = 'https://qwd.jd.com/fcgi-bin/qwd_coupon_query?g_tk={}&sku={}'
        return self.searchSkuList(',', SEARCH_COUPON_URL_TEMPLATE, 'data', itemIds=itemIds, itemId=itemId)

    def retrieveSkuIdList(self):

        skuIdList = list()

        COUPON_PROMOTION_URL = 'http://qwd.jd.com/fcgi-bin/qwd_actclassify_list?g_tk={}&actid={}'

        G_TK = 1915885660
        actid = 10473

        r = requests.get(COUPON_PROMOTION_URL.format(G_TK, actid))

        obj = json.loads(r.text)
        objs = obj.pop('oItemList')

        for item in objs:
            ids = item.pop('skuIds')
            if 0 == len(ids):
                continue

            idlist = ids.split(',')
            skuIdList.extend(idlist)

        print 'Retrieve', len(skuIdList), 'SKUs'
        return skuIdList

    def update(self):

        skuIdList = self.retrieveSkuIdList()
        self.skuList, self.skuIdList, self.newSkuIdList = self.retrieveSkuList(skuIdList)

        self.updateDb('CouponTable', self.skuIdList)

    def getSkuId(self, param):
        return param['skuId']

    def create(self, param):

        if self.db.findOne('CouponTable', skuid=self.getSkuId(param)):
            # Already exists
            return None

        coupon = Coupon(param)
        coupon.insert(self.db, 'CouponTable')

        return coupon

class DiscountManager(SkuManagerBase):

    def __init__(self, configFile, db):
        SkuManagerBase.__init__(self, configFile, db)

    def search(self, itemIds=None, itemId=None):
        SEARCH_DISCOUNT_URL_TEMPLATE = 'http://qwd.jd.com/fcgi-bin/qwd_discount_query?g_tk={}&vsku={}'
        return self.searchSkuList(',', SEARCH_DISCOUNT_URL_TEMPLATE, 'skulist', itemIds=itemIds, itemId=itemId)

    def getSkuId(self, param):
        return param['skuid']

    def create(self, param):

        if self.db.findOne('DiscountTable', skuid=self.getSkuId(param)):
            # Already exists
            return None

        discount = Discount(param)
        discount.insert(self.db, 'DiscountTable')

        return discount

    def update(self):

        skuIdList = self.retrieveSkuIdList()
        self.skuList, self.skuIdList, self.newSkuIdList = self.retrieveSkuList(skuIdList)

        self.updateDb('DiscountTable', self.skuIdList)

    def retrieveSkuIdList(self):

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

