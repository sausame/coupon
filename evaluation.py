#!/usr/bin/env python
# -*- coding:utf-8 -*-

import random
import time

from base import Sku, SkuInformation, Special
from datetime import timedelta, datetime
from history import PriceHistoryManager
from nlp import NLP
from qwd import QWD
from utils import getchar, UrlUtils, reprDict
from validation import Validation

class Evaluation:

    VERSION = 1.0

    COUPON_SQL = ''' SELECT CouponTable.skuid, CouponTable.cutPrice, CouponTable.link AS couponLink,
                          CouponTable.validBeginTime, CouponTable.validEndTime,
                         SkuTable.price, SkuTable.comRate, HistoryTable.list AS historyList
                     FROM `CouponTable` 
                     INNER JOIN SkuTable ON SkuTable.skuid = CouponTable.skuid
                     INNER JOIN HistoryTable ON HistoryTable.skuid = CouponTable.skuid
                     WHERE CouponTable.couponValid = 1'''

    DISCOUNT_SQL = ''' SELECT DiscountTable.skuid, DiscountTable.cutPrice,
                           SkuTable.price, SkuTable.comRate, HistoryTable.list AS historyList
                       FROM `DiscountTable` 
                       INNER JOIN SkuTable ON SkuTable.skuid = DiscountTable.skuid
                       INNER JOIN HistoryTable ON HistoryTable.skuid = DiscountTable.skuid
                       WHERE DiscountTable.haveDiscount = 1'''

    SECKILL_SQL = ''' SELECT SeckillTable.skuid, SeckillTable.cutPrice,
                          SeckillTable.startTime, SeckillTable.endTime,
                          SkuTable.price, SkuTable.comRate, HistoryTable.list AS historyList
                      FROM `SeckillTable` 
                      INNER JOIN SkuTable ON SkuTable.skuid = SeckillTable.skuid
                      INNER JOIN HistoryTable ON HistoryTable.skuid = SeckillTable.skuid
                      WHERE 1'''

    def __init__(self, configFile, db=None):

        self.configFile = configFile
        self.db = db

        self.qwd = QWD(configFile)

        UrlUtils.init(configFile)
        Validation.init(configFile)

        NLP.init(configFile)

    def update(self):

        WHERE_CONDITION = ''' WHERE skuid NOT IN ( SELECT CouponTable.skuid FROM CouponTable )
                  AND skuid NOT IN ( SELECT DiscountTable.skuid FROM DiscountTable )
                  AND skuid NOT IN ( SELECT SeckillTable.skuid FROM SeckillTable )'''

        tableNames = ['SkuTable', 'InformationTable']

        for tableName in tableNames:

            sql = 'SELECT COUNT(*) AS num FROM {} {}'.format(tableName, WHERE_CONDITION)
            result = self.db.query(sql)

            if result is None:
                continue

            for row in result:
                print 'Delete', row['num'], 'records in', tableName

            sql = 'DELETE FROM {} {}'.format(tableName, WHERE_CONDITION)
            self.db.query(sql)

    def evaluate(self):

        self.specialList = list()
        self.inforList = list()

        sqlDict = {'CouponTable': Evaluation.COUPON_SQL,
                'DiscountTable': Evaluation.DISCOUNT_SQL,
                'SeckillTable': Evaluation.SECKILL_SQL}

        condition = ' AND {}.skuid NOT IN (SELECT skuid FROM InformationTable) '

        for tableName in sqlDict.keys():

            result = self.db.query('SELECT id FROM InformationTable LIMIT 1')

            sql = sqlDict[tableName]

            if result is not None:
                sql += condition.format(tableName)

            result = self.db.query(sql)

            if result is None:
                continue

            print '    ', 'Lowest'.rjust(12), 'Cut-Price'.rjust(12), 'Avg-Price'.rjust(12), 'Cata-Price'.rjust(12)

            for row in result:

                infor = SkuInformation(row, Evaluation.VERSION)
                infor.update()

                if infor.priceCorrected:
                    print '***',
                else:
                    print '   ',

                print '{}'.format(infor.data['lowestPrice']).rjust(12),
                print '{}'.format(infor.data['cutPrice']).rjust(12),
                print '{}'.format(infor.data['avgPrice']).rjust(12),
                print '{}'.format(infor.data['price']).rjust(12)

                infor.insert(self.db, 'InformationTable')

                self.inforList.append(infor)

        print len(self.inforList)

    def search(self, key, price=None):

        def isMatched(title, key):

            keywords = NLP.getKeywords(title)

            if keywords is None:
                # XXX: Should it return true?
                return True

            for keyword in keywords:

                if keyword is None:
                    # XXX: Should it return true?
                    return True

                if key in keyword['keyword']:
                    return True

            print '"', title, '" doesn\'t match "', key, '"'

            return False


        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        sql = ''' SELECT InformationTable.id, SkuTable.skuid,
                      InformationTable.lowestPrice, InformationTable.cutPrice,
                      InformationTable.avgPrice, SkuTable.price, 
                      InformationTable.goodCnt, InformationTable.allCnt, InformationTable.percentOfGoodComments,
                      SkuTable.salecount, InformationTable.comRate,
                      InformationTable.totalDays, InformationTable.weight,
                      SkuTable.title, InformationTable.slogan, SkuTable.skuimgurl,
                      InformationTable.couponLink, InformationTable.commentList,
                      InformationTable.startTime, InformationTable.endTime
                  FROM InformationTable 
                  LEFT OUTER JOIN SkuTable ON SkuTable.skuid = InformationTable.skuid 
                  WHERE SkuTable.title LIKE \'%{}%\'
                      AND (InformationTable.endTime IS NULL
                            OR InformationTable.endTime > '{}')'''.format(key, now)

        if price is not None and isinstance(price, tuple):
            sql += ''' AND InformationTable.cutPrice >= {}
                       AND InformationTable.cutPrice <= {}'''.format(price[0], price[1])

        sql += ' ORDER BY SkuTable.salecount DESC'

        result = self.db.query(sql)

        if result is None:
            return None

        specialList = list()

        for row in result:

            if not isMatched(row['title'], key):
                continue

            special = Special(row)
            special.update()
            specialList.append(special)

        return specialList

    def output(self):

        now = datetime.now()

        startTime = now.strftime('%Y-%m-%d %H:%M:%S')
        endTime = (now + timedelta(hours=2)).replace(minute=0,
                second=0, microsecond=0).strftime('%Y-%m-%d %H:%M:%S')

        sql = ''' SELECT COUNT(InformationTable.id) AS num
                  FROM InformationTable 
                  LEFT OUTER JOIN SkuTable ON SkuTable.skuid = InformationTable.skuid 
                  WHERE InformationTable.outputTime <= '{0}'
                      AND InformationTable.cutPrice <= InformationTable.lowestPrice
                      AND InformationTable.totalDays > 30
                      AND ((InformationTable.startTime <= '{0}' AND InformationTable.endTime >= '{1}')
                          OR InformationTable.startTime IS NULL OR InformationTable.endTime IS NULL)
                  '''.format(startTime, endTime) #

        result = self.db.query(sql)

        if result is None:
            return None

        num = 0

        for row in result:
            num = row['num']

        print 'Found', num, 'SKUs between', startTime, 'and', endTime

        if num is 0:
            return None

        sql = ''' SELECT InformationTable.id, SkuTable.skuid,
                      InformationTable.lowestPrice, InformationTable.cutPrice,
                      InformationTable.avgPrice, SkuTable.price, 
                      InformationTable.goodCnt, InformationTable.allCnt, InformationTable.percentOfGoodComments,
                      SkuTable.salecount, InformationTable.comRate,
                      InformationTable.totalDays, InformationTable.weight,
                      SkuTable.title, InformationTable.slogan, SkuTable.skuimgurl,
                      InformationTable.couponLink, InformationTable.commentList,
                      InformationTable.outputTime, InformationTable.startTime, InformationTable.endTime
                  FROM InformationTable 
                  LEFT OUTER JOIN SkuTable ON SkuTable.skuid = InformationTable.skuid 
                  WHERE InformationTable.outputTime <= '{0}'
                      AND InformationTable.cutPrice <= InformationTable.lowestPrice
                      AND InformationTable.totalDays > 30
                      AND ((InformationTable.startTime <= '{0}' AND InformationTable.endTime >= '{1}')
                          OR InformationTable.startTime IS NULL OR InformationTable.endTime IS NULL)
                  ORDER BY InformationTable.endTime ASC,
                      `InformationTable`.`weight` ASC 
                  LIMIT 1 '''.format(startTime, endTime) #

        result = self.db.query(sql)

        if result is None:
            return None

        for row in result:
            special = Special(row)
            special.update(self.db, 'InformationTable')

            return special

        return None

    def explore(self, key, price=None):

        results = self.qwd.search(key, sortByType=2, orderType=1)
        if results is None:
            return None

        priceHistoryManager = PriceHistoryManager()
        specialList = list()

        for result in results:
            sku = Sku(result)
            priceHistoryData = priceHistoryManager.create(sku.data)

            if priceHistoryData is None:
                continue

            data = { 'skuid': sku.data['skuid'],
                    'cutPrice': sku.data['price'],
                    'price': sku.data['price'],
                    'comRate': sku.data['comRate'],
                    'historyList': priceHistoryData.data['list']}

            infor = SkuInformation(data, Evaluation.VERSION)
            infor.update()

            data = dict()
            data.update(sku.data)
            data.update(infor.data)

            special = Special(data)
            special.update()

            specialList.append(special)

        return specialList

    def smartSearch(self, content):

        def getKey(content):

            tokens = NLP.getMorphology(content)

            for token in tokens:

                if token is None:
                    break

                if u'名词' == token['wtype']:
                    return token['word']

            return content

        key = getKey(content)
        print 'Searching "', key, '"'

        specialList = list()

        localList = self.search(key)
        if localList is not None:
            specialList.extend(localList)

        remoteList = self.explore(key)
        if remoteList is not None:
            specialList.extend(remoteList)

        return specialList

