#!/usr/bin/env python
# -*- coding:utf-8 -*-

import random
import time

from base import SkuInformation, Special
from datetime import timedelta, datetime
from qwd import QWD
from utils import getchar, UrlUtils

class Evaluation:

    VERSION = 1.0

    COUPON_SQL = ''' SELECT CouponTable.skuid, CouponTable.specialPrice, CouponTable.link AS couponLink,
                          CouponTable.validBeginTime, CouponTable.validEndTime,
                         SkuTable.price, SkuTable.comRate, HistoryTable.list AS historyList
                     FROM `CouponTable` 
                     INNER JOIN SkuTable ON SkuTable.skuid = CouponTable.skuid
                     INNER JOIN HistoryTable ON HistoryTable.skuid = CouponTable.skuid
                     WHERE CouponTable.couponValid = 1'''

    DISCOUNT_SQL = ''' SELECT DiscountTable.skuid, DiscountTable.specialPrice,
                           SkuTable.price, SkuTable.comRate, HistoryTable.list AS historyList
                       FROM `DiscountTable` 
                       INNER JOIN SkuTable ON SkuTable.skuid = DiscountTable.skuid
                       INNER JOIN HistoryTable ON HistoryTable.skuid = DiscountTable.skuid
                       WHERE DiscountTable.haveDiscount = 1'''

    SECKILL_SQL = ''' SELECT SeckillTable.skuid, SeckillTable.specialPrice,
                          SeckillTable.startTime, SeckillTable.endTime,
                          SkuTable.price, SkuTable.comRate, HistoryTable.list AS historyList
                      FROM `SeckillTable` 
                      INNER JOIN SkuTable ON SkuTable.skuid = SeckillTable.skuid
                      INNER JOIN HistoryTable ON HistoryTable.skuid = SeckillTable.skuid'''

    def __init__(self, configFile, db):

        self.configFile = configFile
        self.db = db

        self.qwd = QWD(configFile)
        self.qwd.login()

        UrlUtils.init(configFile)

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

            for row in result:

                infor = SkuInformation(row, Evaluation.VERSION)

                infor.data['used'] = False
                infor.update()

                infor.insert(self.db, 'InformationTable')

                self.inforList.append(infor)

        print len(self.inforList)

    def output(self):

        now = datetime.now()

        startTime = now.strftime('%Y-%m-%d %H:%M:%S')
        endTime = (now + timedelta(hours=2)).replace(minute=0,
                second=0, microsecond=0).strftime('%Y-%m-%d %H:%M:%S')

        sql = ''' SELECT InformationTable.id, SkuTable.skuid,
                      InformationTable.specialPrice, InformationTable.avgPrice, SkuTable.price, 
                      InformationTable.goodCnt, InformationTable.allCnt, InformationTable.percentOfGoodComments,
                      SkuTable.salecount, InformationTable.comRate,
                      InformationTable.totalDays, InformationTable.weight,
                      SkuTable.title, InformationTable.slogan,
                      InformationTable.couponLink, InformationTable.commentList,
                      InformationTable.startTime, InformationTable.endTime
                  FROM InformationTable 
                  LEFT OUTER JOIN SkuTable ON SkuTable.skuid = InformationTable.skuid 
                  WHERE NOT InformationTable.used
                      AND InformationTable.specialPrice <= InformationTable.lowestPrice
                      AND InformationTable.totalDays > 30
                      AND ((InformationTable.startTime <= '{}' AND InformationTable.endTime >= '{}')
                          OR InformationTable.startTime IS NULL OR InformationTable.endTime IS NULL)
                  ORDER BY InformationTable.endTime ASC,
                      `InformationTable`.`weight` ASC 
                  LIMIT 1 '''.format(startTime, endTime) #

        result = self.db.query(sql)

        if result is None:
            return False

        for row in result:
            special = Special(row)
            special.update(self.qwd, self.db, 'InformationTable')
            print special
            return True

        return False

