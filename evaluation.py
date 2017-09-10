#!/usr/bin/env python
# -*- coding:utf-8 -*-

from base import Special

class Evaluation:

    VERSION = 1.0

    COUPON_SQL = ''' SELECT CouponTable.skuid, CouponTable.specialPrice, CouponTable.link as couponLink,
                          CouponTable.validBeginTime, CouponTable.validEndTime,
                         SkuTable.price, SkuTable.comRate, HistoryTable.list 
                     FROM `CouponTable` 
                     INNER JOIN SkuTable ON SkuTable.skuid = CouponTable.skuid
                     INNER JOIN HistoryTable ON HistoryTable.skuid = CouponTable.skuid'''

    DISCOUNT_SQL = ''' SELECT DiscountTable.skuid, DiscountTable.specialPrice,
                           SkuTable.price, SkuTable.comRate, HistoryTable.list 
                       FROM `DiscountTable` 
                       INNER JOIN SkuTable ON SkuTable.skuid = DiscountTable.skuid
                       INNER JOIN HistoryTable ON HistoryTable.skuid = DiscountTable.skuid'''

    SECKILL_SQL = ''' SELECT SeckillTable.skuid, SeckillTable.specialPrice,
                          SeckillTable.startTime, SeckillTable.endTime,
                          SkuTable.price, SkuTable.comRate, HistoryTable.list
                      FROM `SeckillTable` 
                      INNER JOIN SkuTable ON SkuTable.skuid = SeckillTable.skuid
                      INNER JOIN HistoryTable ON HistoryTable.skuid = SeckillTable.skuid'''

    def __init__(self, configFile, db):

        self.configFile = configFile
        self.db = db

    def evaluate(self):

        self.specialList = list()

        sqls = [Evaluation.COUPON_SQL, Evaluation.DISCOUNT_SQL, Evaluation.SECKILL_SQL]

        for sql in sqls:
            result = self.db.query(sql)

            if result is None:
                continue

            for row in result:
                special = Special(row, Evaluation.VERSION)
                special.update()

                self.db.insert('SpecialTable', special.data, ['skuid'])

                self.specialList.append(special)

        print len(self.specialList)

