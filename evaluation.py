#!/usr/bin/env python
# -*- coding:utf-8 -*-

from base import Special

class Evaluation:

    VERSION = 1.0

    def __init__(self, configFile, db):

        self.configFile = configFile
        self.db = db

        self.specialList = list()

    def evaluateCoupon(self):

        sql = ''' SELECT CouponTable.skuid, CouponTable.specialPrice, CouponTable.link as couponLink,
                      SkuTable.price, SkuTable.comRate, HistoryTable.list 
                  FROM `CouponTable` 
                  INNER JOIN SkuTable ON SkuTable.skuid = CouponTable.skuid
                  INNER JOIN HistoryTable ON HistoryTable.skuid = CouponTable.skuid'''

        result = self.db.query(sql)
        if result is None:
            return

        for row in result:
            special = Special(row, Evaluation.VERSION)
            special.update()
            self.specialList.append(special)
            print special

    def evaluateDiscount(self):
        sql = ''' SELECT DiscountTable.skuid, DiscountTable.specialPrice,
                      SkuTable.price, SkuTable.comRate, HistoryTable.list 
                  FROM `DiscountTable` 
                  INNER JOIN SkuTable ON SkuTable.skuid = DiscountTable.skuid
                  INNER JOIN HistoryTable ON HistoryTable.skuid = DiscountTable.skuid'''

        result = self.db.query(sql)
        if result is None:
            return

        for row in result:
            special = Special(row, Evaluation.VERSION)
            special.update()
            self.specialList.append(special)
            print special

    def evaluateSeckill(self):
        sql = ''' SELECT SeckillTable.skuid, SeckillTable.specialPrice,
                      SeckillTable.startTime, SeckillTable.endTime,
                      SkuTable.price, SkuTable.comRate, HistoryTable.list
                  FROM `SeckillTable` 
                  INNER JOIN SkuTable ON SkuTable.skuid = SeckillTable.skuid
                  INNER JOIN HistoryTable ON HistoryTable.skuid = SeckillTable.skuid'''

        result = self.db.query(sql)
        if result is None:
            return

        for row in result:
            special = Special(row, Evaluation.VERSION)
            special.update()
            self.specialList.append(special)
            print special

    def evaluate(self):

        self.evaluateCoupon()
        self.evaluateDiscount()
        self.evaluateSeckill()

    def store(self):
        pass

